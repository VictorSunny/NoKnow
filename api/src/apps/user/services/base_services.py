from urllib.parse import unquote
from uuid import UUID

import redis.asyncio as redis

from fastapi import WebSocketException

from sqlalchemy import or_
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select, func

from src.caching.services.redis_user_caching import get_user_from_cache, set_user_cache
from src.caching.services.redis_chatroom_caching import (
    clear_chatroom_cache,
    clear_chatroom_cache,
)
from src.apps.user.schemas.base_schemas import (
    FriendshipStatus,
    RawUserList,
    UserBasic,
    UserComplete,
    UserFrienshipStatus,
    UserRoleChoices,
    UserSortBy,
)
from src.apps.user.services.model_services import (
    add_friend_rel,
    add_friend_request_rel,
    check_friend_rel,
    check_friend_request_rel,
    get_user_friend_count,
    remove_friend_rel,
    remove_friend_request_rel,
)
from src.generics.schemas import MessageResponse, SortOrder
from src.db.models import (
    Chatroom,
    User,
    UserChatroomLink,
    UserFriendship,
    UserFriendshipRequest,
)
from src.exceptions.http_exceptions import (
    http_raise_not_found,
    http_raise_unprocessable_entity,
)
from src.utilities.utilities import (
    decode_uri_string_to_list,
    offset_by_page,
)

from logging import getLogger

logger = getLogger(__name__)


# USER CHECK FUNCTIONS -------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------


async def get_user_by_email(
    email: str, db: AsyncSession, r_client: redis.Redis
) -> User:
    """
    Returns `User` by `email`.
    """
    user = None
    user_cache = await get_user_from_cache(id=email, r_client=r_client)
    if user_cache:
        user = user_cache
    else:
        query = select(User).where(func.lower(User.email) == email.lower())
        query_result = await db.execute(query)
        user = query_result.scalar_one_or_none()
        if user:
            await set_user_cache(user=user, r_client=r_client)

    if not user:
        http_raise_not_found(reason="Anonymous user does not exist.")

    return user


async def get_user_by_username(
    username: str,
    db: AsyncSession,
    r_client: redis.Redis,
    websocket_conn: bool | None = False,
) -> User:
    """
    Returns `User` by `username`.
    """
    user = None

    user_cache = await get_user_from_cache(id=username, r_client=r_client)
    if user_cache:
        user = user_cache
    else:
        query = select(User).where(func.lower(User.username) == username.lower())
        query_result = await db.execute(query)
        user = query_result.scalar_one_or_none()
        if user:
            await set_user_cache(user=user, r_client=r_client)

    if not user:
        if websocket_conn:
            raise WebSocketException(404, "Anonymous user does not exist.")
        http_raise_not_found(reason="Anonymous user does not exist.")

    return user


async def get_user_by_uid(id: UUID, db: AsyncSession, r_client: redis.Redis) -> User:
    """
    Returns `User` by `id`.
    """
    user = None
    user_cache = await get_user_from_cache(id=id, r_client=r_client)
    if user_cache:
        user = user_cache
    else:
        user = await db.get(User, id)
        if user:
            await set_user_cache(user=user, r_client=r_client)

    if not user:
        http_raise_not_found(reason="Anonymous user does not exist.")

    return user


# END OF USER CHECK FUNCTIONS -------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------


async def get_user_details(
    user: User, username: str, db: AsyncSession, r_client: redis.Redis
) -> UserBasic | UserComplete:
    """
    Returns user details.

    Args:
        user: Logged in `User`
        username: String - for user details to return
        db: Asynchronous database connection instance
    Raises:
        HTTPException 404: `User` with `username` does not exist
    """
    if username:
        user = await get_user_by_username(username=username, db=db, r_client=r_client)
        response = UserBasic(**user.model_dump())
    else:
        response = UserComplete(**user.model_dump())

    return response


async def send_friend_request(
    user: User, candidate_uid: UUID, db: AsyncSession, r_client: redis.Redis
) -> MessageResponse:
    """
    Sends friend request from logged in `User` to candidate `User`.

    Args:
        user: Logged in `User`
        candidate_uid: UUID for candidate `User` to receive friend request
        db: Asynchronous database connection instance

    Raises:
        HTTPException:
            404: Candidate `User` does not exist
            422:
                -Logged in `User` is trying to perform action on self
                -Logged in `User` is already a friend to candidate `User`
                -Logged in `User` has already sent a friend request to candidate `User`
                -Candidate `User` has already sent a friend request to Logged in `User` who has not yet responded
    """
    candidate = await get_user_by_uid(id=candidate_uid, db=db, r_client=r_client)

    candidate_is_friend = await check_friend_rel(user=user, to_check=candidate, db=db)

    # check if candidate has sent user a friend request
    candidate_sent_user_friend_request = await check_friend_request_rel(
        from_user=candidate, to_user=user, db=db
    )
    # check if user has sent canidate a friend request
    user_sent_candidate_friend_request = await check_friend_request_rel(
        from_user=user, to_user=candidate, db=db
    )

    logger.info(f"sending friend request from user: {user.uid} to {candidate.uid}")
    if candidate.uid == user.uid:
        http_raise_unprocessable_entity(
            reason="User cannot send friend request to self."
        )
    if candidate_is_friend:
        http_raise_unprocessable_entity(reason="User is already a friend.")
    if candidate_sent_user_friend_request:
        http_raise_unprocessable_entity(
            reason="Friend request is pending. Accept request instead."
        )
    if user_sent_candidate_friend_request:
        http_raise_unprocessable_entity(f"Friend request already sent.")

    await add_friend_request_rel(from_user=user, to_user=candidate, db=db)

    return {"message": "Friend request sent successfully."}


async def cancel_friend_request(
    user: User, candidate_uid: UUID, db: AsyncSession, r_client: redis.Redis
) -> MessageResponse:
    """
    Cancels friend request sent from logged in `User` to candidate `User`.

    Args:
        user: Logged in `User`
        candidate_uid: UUID for candidate `User` to withdraw friend request from
        db: Asynchronous database connection instance

    Raises:
        HTTPException:
            404: Candidate `User` does not exist
            422:
                -Logged in `User` is trying to perform action on self
                -Logged in `User has not sent a friend request to candidate `User`
    """
    candidate = await get_user_by_uid(id=candidate_uid, db=db, r_client=r_client)

    if user.uid == candidate.uid:
        http_raise_unprocessable_entity(
            reason="User cannot perform this action on self."
        )

    # check if user has sent canidate a friend request
    user_sent_candidate_friend_request = await check_friend_request_rel(
        from_user=user, to_user=candidate, db=db
    )

    logger.info(
        f"cancelling friend request sent to user: {candidate.uid} from user: {user.uid}"
    )
    if not user_sent_candidate_friend_request:
        http_raise_unprocessable_entity(
            reason="Unable to cancel friend request as none exists."
        )

    await remove_friend_request_rel(from_user=user, to_user=candidate, db=db)

    await db.commit()
    return {"message": "successfully cancelled friend request."}


async def accept_friend_request(
    user: User, candidate_uid: UUID, db: AsyncSession, r_client: redis.Redis
) -> MessageResponse:
    """
    Allows logged in `User` to accept friend request from candidate `User`,
    then adds both `User`s to each other's respective friend lists.

    Args:
        user: Logged in `User`
        candidate_uid: UUID for candidate `User` to accept friend request from
        db: Asynchronous database connection instance

    Raises:
        HTTPException:
            404: Candidate `User` does not exist
            422:
                -Logged in `User` is trying to perform action on self
                -Candidate `User` sent no friend request to logged in `User`
                -Logged in `User` and candidate `User` are already friends
                -Logged in `User` friends count has reached the maximum allowed limit
    """
    candidate = await get_user_by_uid(id=candidate_uid, db=db, r_client=r_client)

    logger.info(f"user: {user.uid} accepting friend request of user: {candidate.uid}")

    # check if candidate is friends with user
    user_is_friend = await check_friend_rel(user=candidate, to_check=user, db=db)
    # check if user is friends with candidate
    candidate_is_friend = await check_friend_rel(user=user, to_check=candidate, db=db)

    # check if candidate has sent user a friend request
    candidate_sent_user_friend_request = await check_friend_request_rel(
        from_user=candidate, to_user=user, db=db
    )

    # get user friend count
    user_friend_count = await get_user_friend_count(user=user, db=db)

    if not candidate_sent_user_friend_request:
        http_raise_unprocessable_entity(
            reason="Unable to accept friend request as none exists."
        )

    if user_is_friend and candidate_is_friend:
        http_raise_unprocessable_entity(reason="Candidate is already a friend.")

    if not candidate_is_friend:
        # add candidate to friend list of logged in user
        max_friends_allowed = 100
        if user_friend_count == max_friends_allowed:
            http_raise_unprocessable_entity(
                reason=f"User cannot have more than {max_friends_allowed} friends."
            )
        await add_friend_rel(user=user, candidate=candidate, db=db)
        await remove_friend_request_rel(from_user=candidate, to_user=user, db=db)
    if not user_is_friend:
        # add logged in user to friend list of candidate
        await add_friend_rel(user=candidate, candidate=user, db=db)

    await db.commit()
    return {"message": "Successfully accepted friend request."}


async def reject_friend_request(
    user: User, candidate_uid: UUID, db: AsyncSession, r_client: redis.Redis
) -> MessageResponse:
    """
    Allows logged in `User` to reject friend request from candidate `User`.

    Args:
        user: Logged in `User`
        candidate_uid: UUID for candidate `User` to reject friend request from
        db: Asynchronous database connection instance

    Raises:
        HTTPException:
            404: Candidate `User` does not exist
            422:
                -Logged in `User` is trying to perform action on self
                -Candidate `User` sent no friend request to logged in `User`
    """

    candidate = await get_user_by_uid(id=candidate_uid, db=db, r_client=r_client)
    # raise error if user is trying to perform action on self
    if candidate.uid == user.uid:
        http_raise_unprocessable_entity(
            reason="User is trying to perform action on self."
        )

    # check if candidate has sent user a friend request
    candidate_sent_user_friend_request = await check_friend_request_rel(
        from_user=candidate, to_user=user, db=db
    )

    logger.info(
        f"rejecting friend request of user: {candidate.uid} for user: {user.uid}"
    )

    if not candidate_sent_user_friend_request:
        http_raise_unprocessable_entity(
            reason="Unable to reject. No friend request was sent by this user"
        )

    await remove_friend_request_rel(from_user=candidate, to_user=user, db=db)

    return {"message": "Successfully declined friend request."}


async def remove_friend(
    user: User, candidate_uid: UUID, db: AsyncSession, r_client: redis.Redis
) -> MessageResponse:
    """
    Removes candidate `User` from logged in `User`'s friends,

    Args:
        user: Logged in `User`
        candidate_uid: UUID for candidate `User` to accept friend request from
        db: Asynchronous database connection instance

    Raises:
        HTTPException:
            404: Candidate `User` does not exist
            422:
                -Logged in `User` is trying to perform action on self
                -Logged in `User` and candidate `User` are not friends
    """
    candidate = await get_user_by_uid(id=candidate_uid, db=db, r_client=r_client)

    # raise error if user is trying to perform action on self
    if candidate.uid == user.uid:
        http_raise_unprocessable_entity(
            reason="User is trying to perform action on self."
        )

    # check if candidate is friends with user
    user_is_friend = await check_friend_rel(user=candidate, to_check=user, db=db)
    # check if user is friends with candidate
    candidate_is_friend = await check_friend_rel(user=user, to_check=candidate, db=db)

    # -- LOGGING
    logger.info(f"removing friend: {candidate.uid} for user: {user.uid}")

    if (not candidate_is_friend) and (not user_is_friend):
        http_raise_unprocessable_entity(reason="User is not a friend.")

    # delete chat created between users if any
    query = (
        select(Chatroom)
        .join(UserChatroomLink)
        .where(UserChatroomLink.user_uid.in_([user.uid, candidate.uid]))
        .where(Chatroom.room_type == "personal")
        .group_by(Chatroom.uid)
        .having(func.count(UserChatroomLink.user_uid) == 2)
    )

    query_response = await db.execute(query)
    friend_chatroom = query_response.unique().scalars().first()
    if friend_chatroom:
        await clear_chatroom_cache(id=friend_chatroom.uid, r_client=r_client)
        await db.delete(friend_chatroom)

    # remove users from respective friend lists
    if candidate_is_friend:
        await remove_friend_rel(user=user, candidate=candidate, db=db)
    if user_is_friend:
        await remove_friend_rel(user=candidate, candidate=user, db=db)

    await db.commit()
    return {"message": "Successfully unfriended candidate."}


# END OF USER UPDATE FUNCTIONS ---------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------


# USER RETRIEVAL FUNCTIONS ---------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------


async def get_user_friends(
    user: User,
    db: AsyncSession,
    page: int,
    sort: UserSortBy,
    order: SortOrder,
    search_query: str,
) -> RawUserList:
    """
    Returns logged in `User`'s friends.
    """
    limit = 24
    offset = offset_by_page(page_num=page, limit=limit)
    query = (
        select(User, UserFriendship)
        .join(User, UserFriendship.user_uid == User.uid)
        .where(UserFriendship.friend_uid == user.uid)
        .where(User.uid != user.uid)
        .limit(limit)
        .offset(offset)
    )

    if sort == UserSortBy.DATE:
        query = (
            query.order_by(UserFriendship.created_at.asc())
            if order == SortOrder.ASC
            else query.order_by(UserFriendship.created_at.desc())
        )
    if sort == UserSortBy.USERNAME:
        query = (
            query.order_by(User.username.desc())
            if order == SortOrder.DESC
            else query.order_by(User.username.asc())
        )

    if search_query:
        search_query = unquote(search_query).split(" ")[0]
        query = query.where(
            or_(
                User.username.ilike(f"%{search_query}%"),
                User.first_name.ilike(f"%{search_query}%"),
                User.last_name.ilike(f"%{search_query}%"),
            )
        )

    executed_query = await db.execute(query)
    user_friends = executed_query.unique().scalars().all()
    response = {"users": user_friends}
    return response


async def get_user_friend_requests(
    user: User,
    sort: UserSortBy,
    order: SortOrder,
    db: AsyncSession,
    page: int | None = 1,
) -> RawUserList:
    """
    Returns logged in `User`'s friend requests.
    """
    limit = 24
    offset = offset_by_page(page_num=page, limit=limit)
    query = (
        select(User, UserFriendshipRequest)
        .join(User, UserFriendshipRequest.request_friend_uid == User.uid)
        .where(UserFriendshipRequest.user_uid == user.uid)
        .limit(limit)
        .offset(offset)
    )
    if sort == UserSortBy.DATE:
        query = (
            query.order_by(UserFriendshipRequest.created_at.asc())
            if order == SortOrder.ASC
            else query.order_by(UserFriendshipRequest.created_at.desc())
        )
    else:
        query = (
            query.order_by(User.username.desc())
            if order == SortOrder.DESC
            else query.order_by(User.username.asc())
        )
    executed_query = await db.execute(query)
    user_friend_requests = executed_query.unique().scalars().all()
    response = {"users": user_friend_requests}
    return response


async def get_user_sent_friend_requests(
    user: User,
    sort: UserSortBy,
    order: SortOrder,
    db: AsyncSession,
    page: int | None = 1,
) -> RawUserList:
    """
    Returns dict containing `User`s that logged in `User` has sent a friend request to.
    """
    limit = 24
    offset = offset_by_page(page_num=page, limit=limit)
    query = (
        select(User, UserFriendshipRequest)
        .join(User, UserFriendshipRequest.user_uid == User.uid)
        .where(UserFriendshipRequest.request_friend_uid == user.uid)
        .limit(limit)
        .offset(offset)
    )
    if sort == UserSortBy.DATE:
        query = (
            query.order_by(UserFriendshipRequest.created_at.asc())
            if order == SortOrder.ASC
            else query.order_by(UserFriendshipRequest.created_at.desc())
        )
    else:
        query = (
            query.order_by(User.username.desc())
            if order == SortOrder.DESC
            else query.order_by(User.username.asc())
        )
    executed_query = await db.execute(query)
    user_sent_friend_requests = executed_query.unique().scalars().all()
    response = {"users": user_sent_friend_requests}
    return response


async def check_frienship_status_by_username(
    user: User, candidate_username: str, db: AsyncSession, r_client: redis.Redis
) -> FriendshipStatus:
    """
    Returns friendship status between logged in `User` and candidate `User`.

    Args:
        user: Logged in `User` instance
        candidate_username: String value for candidate `User`
        db: Asynchronous database connection instance
    """
    if user.username == candidate_username:
        http_raise_unprocessable_entity(reason="You are not your friend.")

    candidate = await get_user_by_username(
        username=candidate_username, db=db, r_client=r_client
    )

    # check if user is friends with candidate
    candidate_is_friend = await check_friend_rel(user=user, to_check=candidate, db=db)

    # check if candidate has sent user a friend request
    candidate_sent_user_friend_request = await check_friend_request_rel(
        from_user=candidate, to_user=user, db=db
    )
    # check if user has sent canidate a friend request
    user_sent_candidate_friend_request = await check_friend_request_rel(
        from_user=user, to_user=candidate, db=db
    )

    friendship_status = UserFrienshipStatus.UNDFRIENDED
    if candidate_is_friend:
        friendship_status = UserFrienshipStatus.FRIENDED
    if candidate_sent_user_friend_request:
        friendship_status = UserFrienshipStatus.PENDING
    if user_sent_candidate_friend_request:
        friendship_status = UserFrienshipStatus.REQUESTED

    response = {"friendship_status": friendship_status}
    return response


async def search_users(query: str, user: User, db: AsyncSession) -> RawUserList:
    """
    Searches database for `User`s matching search `query`.

    Args:
        query: String value by which search is carried out
        user: Logged in `User` instance
        db: Asynchronous database connection instance
    """
    query_list = decode_uri_string_to_list(query)[:4]
    logger.info(f"searching for users")
    query = (
        select(User)
        .where(User.uid != user.uid)
        .where(User.is_hidden == False)
        .where(User.role == UserRoleChoices.USER)
        .where(
            (func.lower(User.first_name).in_(query_list))
            | (func.lower(User.last_name).in_(query_list))
            | (func.lower(User.username).in_(query_list))
        )
    )

    executed_query = await db.execute(query)
    all_users = executed_query.unique().scalars().all()

    response = {"users": all_users}
    return response


# END OF USER RETRIEVAL FUNCTIONS ---------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------
