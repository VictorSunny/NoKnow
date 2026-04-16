import select
from urllib.parse import unquote
from uuid import UUID
from sqlalchemy import or_
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import aliased

import redis.asyncio as redis

from src.caching.services.redis_chatroom_caching import (
    set_chatroom_cache,
)
from src.apps.chat.services.model_services import (
    add_chatroom_user_banned_rel,
    add_chatroom_user_member_rel,
    add_chatroom_user_moderator_rel,
    check_chatroom_user_banned_rel,
    get_chatroom_moderator_user_count,
    remove_chatroom_user_banned_rel,
    remove_chatroom_user_member_rel,
    remove_chatroom_user_moderator_rel,
)
from src.generics.schemas import MessageResponse, SortOrder
from src.apps.user.schemas.base_schemas import RawUserList, UserSortBy
from src.apps.chat.schemas.base_schemas import (
    ChatroomType,
    ChatroomMemberRole,
    ChatroomPrivatePublicType,
    ChatroomMemberRole,
    ChatroomsSort,
    RawChatroomList,
)
from src.utilities.utilities import offset_by_page
from src.generics.validation_services import error_if_model_password_incorrect
from src.apps.user.services.base_services import get_user_by_uid
from src.apps.chat.services.base_services import (
    check_chatroom_user_member_rel,
    check_chatroom_user_moderator_rel,
    create_announcement_in_chat,
    get_chatroom,
    disallow_action_for_public_chatroom,
)
from src.db.models import (
    Chatroom,
    User,
    UserChatroomBannedLink,
    UserChatroomLink,
    UserChatroomModeratorsLink,
)
from src.exceptions.http_exceptions import (
    http_raise_forbidden,
    http_raise_unprocessable_entity,
)
from logging import getLogger

logger = getLogger(__name__)

# INTEGRATED SERVICES FOR PRIVATE CHATROOM OPERATIONS


async def join_chatroom(
    id: UUID,
    user: User,
    db: AsyncSession,
    r_client: redis.Redis,
    chatroom_password: str | None = None,
) -> MessageResponse:
    """
    Adds logged in `User` to `Chatroom` members.
    Raise error if user is banned from `Chatroom`.

    Protected `Chatroom`s should require that `chatroom_password` is not Null,
    and is valid for the matching `Chatroom` instance.

    Non-proteced `Chatroom` should not require password to join.
    `chatroom_password` input should be completely ignored for non-protected chatroom.
    Should not raise error whether it is valid or invalid for the matching `Chatroom` instance.

    Args:
        id: UUID for matching chatroom
        user: Logged in `User` instance
        db: Asynchronous database connection instance
        chatroom_password: *optional* string password for verfication to join `Chatroom`

    Raises:
        HTTPException:
            403:
                -`user` is banned from `Chatroom`
            422:
                -Incorrect provided chatroom password
                -logged in `User` is already a member of `Chatroom`
    """
    chatroom = await get_chatroom(
        chatroom_identifier=id,
        use_case=f"add member",
        from_cache=False,
        db=db,
        r_client=r_client,
    )

    logger.info(f"user: {user.uid} joining chatroom: {chatroom.uid}")

    # raise error if chatroom is private and password is Null
    if (chatroom.room_type == ChatroomType.PRIVATE) and not chatroom_password:
        http_raise_forbidden(
            reason="Chatroom is private. Please enter password and retry."
        )

    # check entered password is valid if chatroom is private and chatroom has a password
    if chatroom.room_type == ChatroomType.PRIVATE:
        # announce that user has joined chat without password if chatroom has no password
        if not chatroom.password:
            await create_announcement_in_chat(
                message_content=f"{user.username} became a member without password.",
                chatroom=chatroom,
                db=db,
            )
        # else check that password entered by user is valid
        else:
            await error_if_model_password_incorrect(
                model_name="chatroom",
                password=chatroom_password,
                hashed_password=chatroom.password,
            )

    # raise exception if user has been banned from joining chatroom
    user_is_banned = await check_chatroom_user_banned_rel(
        user=user, chatroom=chatroom, db=db
    )
    if user_is_banned:
        http_raise_forbidden(reason="User has been banned from this chatroom.")

    # confirm that user is not a member of chatroom befor adding
    user_is_member = await check_chatroom_user_member_rel(
        user=user, chatroom=chatroom, db=db
    )
    if not user_is_member:
        # add user to chatroom and save changes to chatroom
        await add_chatroom_user_member_rel(user=user, chatroom=chatroom, db=db)

        logger.info(f"user successfully joined chatroom")

        if chatroom.room_type == ChatroomType.PRIVATE:
            # create and send announcement on success
            announcement_text = f"@{user.username} became a member"
            await create_announcement_in_chat(
                chatroom=chatroom, message_content=announcement_text, db=db
            )
    else:
        # raise error if user is already a member
        http_raise_unprocessable_entity(
            reason=f"You are already a member of this chatroom."
        )
    db.add(chatroom)
    await db.commit()
    await set_chatroom_cache(chatroom=chatroom, r_client=r_client)
    return {"message": "User successfully joined chatroom."}


async def leave_chatroom(
    user: User, id: UUID, db: AsyncSession, r_client: redis.Redis
) -> MessageResponse:
    """
    Removes logged in `User` from `Chatroom` with matching `id`.

    Removes all relationships shared between the `User` and `Chatroom` instance,
    including member, moderator, creator_successor, and creator relationships.

    Assigns `Chatroom` successor the role of `creator` upon removal of the current creator.

    Args:
        user: Logged in `User` instance
        id: UUID for matching chatroom
        db: Asynchronous database connection instance


    Raises:
        HTTPException:
            403:
                -Logged in `user` instance is not a member of `Chatroom`.
                -`user` is the `creator` of `Chatroom` which has no current successor.
            404:
                -No `Chatroom` with matching `id` exists.
            422:
                -`user` already left `Chatroom with matching `id`.
    """

    chatroom = await get_chatroom(
        chatroom_identifier=id,
        db=db,
        use_case=f"remove user",
        from_cache=False,
        r_client=r_client,
    )
    # check if user is a member
    user_is_member = await check_chatroom_user_member_rel(
        user=user, chatroom=chatroom, db=db
    )
    # confirm that user is a member of chatroom befor removing
    user_is_moderator = await check_chatroom_user_moderator_rel(
        user=user, chatroom=chatroom, db=db
    )

    logger.info(f"user: {user.uid} leaving chatroom")

    # raise error if user trying to leave is not a member of the chatroom
    if not user_is_member:
        http_raise_unprocessable_entity(reason="User already left chatroom.")

    # check if user trying to leave is the creator of the chatroom
    if user.uid == chatroom.creator_uid:
        if (chatroom.room_type == ChatroomPrivatePublicType.PRIVATE) and (
            not chatroom.creator_successor_uid
        ):
            # raise error if the chatroom has no successor
            http_raise_unprocessable_entity(
                f"User is the creator and cannot leave as chatroom has no successor."
            )

        # remove user role as chatroom creator
        chatroom.creator_uid = None

        # assign successor as creator if a successor was appointed
        if chatroom.creator_successor_uid:
            # assign creator_successor the position of creator
            chatroom.creator_uid = chatroom.creator_successor_uid
            # make the creator_successor vacant for new creator to pick a successor
            chatroom.creator_successor_uid = None

            logger.info(f"creator: @{user.username} successfully left chat: {id}")
            # create announcement in chatroom to announce new transfer of ownership
            await create_announcement_in_chat(
                chatroom=chatroom,
                message_content=f"Creator is no longer a member.",
                db=db,
            )

    if user_is_moderator:
        await remove_chatroom_user_moderator_rel(user=user, chatroom=chatroom, db=db)

    if user.uid == chatroom.creator_successor_uid:
        chatroom.creator_successor_uid = None
        logger.info(f"user: {user.uid} successfully left chatroom: {chatroom.uid}")

    await remove_chatroom_user_member_rel(user=user, chatroom=chatroom, db=db)
    await create_announcement_in_chat(
        chatroom=chatroom,
        message_content=f"@{user.username} is no longer a member",
        db=db,
    )

    db.add(chatroom)
    await db.commit()
    await db.refresh(chatroom)

    await set_chatroom_cache(chatroom=chatroom, r_client=r_client)
    return {"message": "User successfully left chatroom."}


async def remove_and_ban_user_from_chat(
    id: UUID, violator_uid: UUID, user: User, db: AsyncSession, r_client: redis.Redis
) -> MessageResponse:
    """
    Removes `User` with matching `violator_uid` from `Chatroom` members, moderators, and creator_successor,
    and bans `violator` from `Chatroom`, preventing the `violator` from joining `Chatroom` again.

    Args:
        id: UUID for matching `Chatroom`
        violator_uid: UUID for `User` to be removed and banned from `Chatroom`
        user: Logged in `User` instance
        db: Asynchronous database connection instance

    Raises:
        HTTPException:
            403:
                --Logged in `User` is trying to perform action on self.
                -`violator` is a moderator or successor, and logged in user not `Chatroom` creator
                -Logged in `User` is not a moderator, nor the creator of `Chatroom`.
                -`violator` is the creator of `Chatroom`.
            404:
                -No `Chatroom` with matching `id` exists.
                -No `User` with matching `forgiven_uid` exists.
            422:
                -`Chatroom` is `public`.
    """
    violator = await get_user_by_uid(id=violator_uid, db=db)
    chatroom = await get_chatroom(
        chatroom_identifier=id,
        use_case=f"remove/ban user: {violator.uid}",
        from_cache=False,
        db=db,
        r_client=r_client,
    )
    await disallow_action_for_public_chatroom(chatroom=chatroom)

    logger.info(
        f"starting ban/remove for user: {violator.uid} in chatroom: {chatroom.uid}"
    )

    # check if user is a moderator
    user_is_moderator = await check_chatroom_user_moderator_rel(
        user=user, chatroom=chatroom, db=db
    )

    # check if user is a member
    violator_is_member = await check_chatroom_user_member_rel(
        user=violator, chatroom=chatroom, db=db
    )
    # check if user is a moderator
    violator_is_moderator = await check_chatroom_user_moderator_rel(
        user=violator, chatroom=chatroom, db=db
    )
    # check if user is banned
    violator_is_banned = await check_chatroom_user_banned_rel(
        user=violator, chatroom=chatroom, db=db
    )

    # check if logged in user has the privilege to remove violator
    if user.uid != chatroom.creator_uid:
        if not user_is_moderator:
            http_raise_forbidden(reason="User is not a moderator.")
        if violator.uid == chatroom.creator_successor_uid:
            http_raise_forbidden(
                reason="User is the chatroom's successor and can only be removed by the creator."
            )
        if violator_is_moderator:
            http_raise_forbidden(
                reason="Only the chatroom's creator can remove a moderator."
            )

    # raise error if violator is the logged in user.
    if violator.uid == user.uid:
        http_raise_forbidden(reason="User cannot remove self.")

    # raise error if violator is the chatroom creator.
    if violator.uid == chatroom.creator_uid:
        http_raise_forbidden(
            reason="User is the chatroom's creator and cannot be removed."
        )

    # add violator to banned users
    if not violator_is_banned:
        await add_chatroom_user_banned_rel(user=violator, chatroom=chatroom, db=db)

    # remove violator from moderators
    if violator_is_moderator:
        await remove_chatroom_user_moderator_rel(
            user=violator, chatroom=chatroom, db=db
        )

    # relieve violator of successor role
    if violator.uid == chatroom.creator_successor_uid:
        chatroom.creator_successor_uid = None
        db.add(chatroom)
        logger.info(
            f"user: {violator.uid} successfully removed as successor for chatroom: {chatroom.uid}"
        )

    # remove violator from members
    if violator_is_member:
        await remove_chatroom_user_member_rel(user=violator, chatroom=chatroom, db=db)

        await create_announcement_in_chat(
            message_content=f"@{violator.username} has been removed by @{user.username}",
            chatroom=chatroom,
            db=db,
        )

    logger.info(f"successfully completed ban/remove of user: {violator.uid}")

    db.add(chatroom)
    await db.commit()
    await db.refresh(chatroom)

    await set_chatroom_cache(chatroom=chatroom, r_client=r_client)
    return {
        "message": f"successfully removed and banned {violator.username} from chatroom"
    }


async def add_and_unban_user_from_chat(
    id: UUID, forgiven_uid: UUID, user: User, db: AsyncSession, r_client: redis.Redis
) -> MessageResponse:
    """
    Adds `User` with matching `forgiven_uid` to members of `Chatroom` with matching `id`.
    Unbans the forgiven `User` from `Chatroom` if previously banned.

    Args:
            id: UUID for matching `Chatroom`
            user: Logged in `User` instance
            db: Asynchronous database connection instance
            forgiven_uid: UUID for `User` to be added and unbanned from `Chatroom`

    Raises:
        HTTPException:
            403:
                -Logged in `User` is trying to perform action on self
                -Logged in `user` instance is not a moderator of `Chatroom`, nor the creator.
            404:
                -No `Chatroom` with matching `id` exists.
                -No `User` with matching `forgiven_uid` exists.
            422:
                -`Chatroom` is `public`.

    """
    forgiven = await get_user_by_uid(id=forgiven_uid, db=db)
    chatroom = await get_chatroom(
        chatroom_identifier=id,
        use_case=f"add/unban user {forgiven.uid}",
        from_cache=False,
        db=db,
        r_client=r_client,
    )
    await disallow_action_for_public_chatroom(chatroom=chatroom)

    logger.info(f"starting add/unban user: {forgiven.uid} for chatroom: {chatroom.uid}")

    # check if user is a moderator
    user_is_moderator = await check_chatroom_user_moderator_rel(
        user=user, chatroom=chatroom, db=db
    )

    # check if forgiven is a member
    forgiven_is_member = await check_chatroom_user_member_rel(
        user=forgiven, chatroom=chatroom, db=db
    )
    # check if forgiven is banned
    forgiven_is_banned = await check_chatroom_user_banned_rel(
        user=forgiven, chatroom=chatroom, db=db
    )

    # raise error is not a moderator, nor the chatroom creator
    if (not user_is_moderator) and (user.uid != chatroom.creator_uid):
        http_raise_forbidden(reason="User is not a moderator.")

    # raise error if forgiven user is logged in user
    if forgiven.uid == user.uid:
        http_raise_unprocessable_entity(
            reason="User cannot perform this action on self."
        )

    if not forgiven_is_member:
        await add_chatroom_user_member_rel(user=forgiven, chatroom=chatroom, db=db)
        await create_announcement_in_chat(
            message_content=f"@{forgiven.username} has been added by @{user.username}",
            chatroom=chatroom,
            db=db,
        )

    if forgiven_is_banned:
        await remove_chatroom_user_banned_rel(user=forgiven, chatroom=chatroom, db=db)

    db.add(chatroom)
    await db.commit()
    await set_chatroom_cache(chatroom=chatroom, r_client=r_client)
    return {"message": f"Successfully added user to chatroom."}


async def get_chatroom_members(
    id: UUID,
    user: User,
    db: AsyncSession,
    r_client: redis.Redis,
    page: int,
    sort: UserSortBy,
    order: SortOrder,
    role: ChatroomMemberRole,
    is_admin_action: bool | None = False,
    search_query: str | None = None,
) -> RawUserList:
    """
    Retrieves all `Chatroom` members.
    Returns only non-hidden members if logged in `User` is a normal member.
    Returns all members, hidden and non-hidden, if logged in `User` is a moderator or `Chatroom` creator.

    Args:
        id: UUID for matching chatroom
        user: Logged in `User` instance
        db: Asynchronous database connection instance
        role: grade of members to be retrieved e.g moderators, normal members, etc
        search_query: *optional* string used to find `Chatroom` with matching name or creator username
        :***

    Raises:
        HTTPException:
            403:
                -Logged in `User` is not a member of `Chatroom`
            404:
                -No `Chatroom` with matching `id` exists
    """
    limit = 24
    offset = offset_by_page(page_num=page, limit=limit)

    chatroom = await get_chatroom(
        chatroom_identifier=id, db=db, use_case="get all members", r_client=r_client
    )
    logger.info(f"retrieving members list for chatroom: {chatroom.uid}")

    # check if user is a member
    user_is_member = await check_chatroom_user_member_rel(
        user=user, chatroom=chatroom, db=db
    )
    # check if user is a moderator
    user_is_moderator = await check_chatroom_user_moderator_rel(
        user=user, chatroom=chatroom, db=db
    )
    # check if user is banned
    user_is_banned = await check_chatroom_user_banned_rel(
        user=user, chatroom=chatroom, db=db
    )

    if not is_admin_action:
        if user_is_banned:
            http_raise_forbidden(reason="User is banned from this chatroom.")
        if not user_is_member:
            http_raise_forbidden(reason="User is not a member of this chatroom.")

    if role == ChatroomMemberRole.CREATOR:
        members = [chatroom.creator] if chatroom.creator else []
        response = {"users": members}
        return response

    link_table = (
        UserChatroomModeratorsLink
        if role == ChatroomMemberRole.MODERATOR
        else (
            UserChatroomBannedLink
            if role == ChatroomMemberRole.REMOVED
            else UserChatroomLink
        )
    )
    query = (
        select(User)
        .join(link_table)
        .where(link_table.chatroom_uid == id)
        .offset(offset)
        .limit(limit)
    )
    # keep private users hidden from normal members
    # only moderators and chatroom creator can see private users
    if (
        (not user_is_moderator)
        and (user.uid != chatroom.creator_uid)
        and (not is_admin_action)
    ):
        query = query.where(User.is_hidden == False)

    # sort users
    if sort == UserSortBy.DATE:
        query = (
            query.order_by(link_table.created_at.asc())
            if order == SortOrder.ASC
            else query.order_by(link_table.created_at.desc())
        )
    else:
        query = (
            query.order_by(User.username.desc())
            if order == SortOrder.DESC
            else query.order_by(User.username.asc())
        )

    # get users matching search query
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
    members = executed_query.scalars().all()

    logger.info(f"successfully retrieved members for chatroom: {chatroom.uid}")

    response = {"users": members}
    return response


async def add_user_to_chatroom_moderators(
    id: UUID, candidate_uid: UUID, user: User, db: AsyncSession, r_client: redis.Redis
) -> RawUserList:
    """
    Add `User` to chatroom moderators.

    Args:
        id: UUID for matching `Chatroom`
        user: Logged in `User` instance
        db: Asynchronous database connection instance
        candidate_uid: UUID for `User` to be added to `Chatroom` moderators

    Raises:
        HTTPException:
            403:
                -Logged in `User` is not `Chatroom`'s creator
            404:
                -No `Chatroom` with matching `id` exists
                -No `User` with matching `candidate_uid` exists
            422:
                -`Chatroom` is `public`
                -Number of `Chatroom` moderators has reached maximum limit
                -Candidate to be added to moderators is not a member of `Chatroom`
                -Candidite is already a moderator of `Chatroom`
    """

    max_chatroom_moderators = 10
    candidate = await get_user_by_uid(id=candidate_uid, db=db)
    chatroom = await get_chatroom(
        chatroom_identifier=id,
        use_case=f"add user to moderators",
        from_cache=False,
        db=db,
        r_client=r_client,
    )
    await disallow_action_for_public_chatroom(chatroom=chatroom)

    moderators_count = await get_chatroom_moderator_user_count(chatroom=chatroom, db=db)

    # check if user is a member
    candidate_is_member = await check_chatroom_user_member_rel(
        user=candidate, chatroom=chatroom, db=db
    )
    # check if user is a moderator
    candidate_is_moderator = await check_chatroom_user_moderator_rel(
        user=candidate, chatroom=chatroom, db=db
    )

    logger.info(f"adding user: {candidate.uid} to chatroom: {chatroom.uid}")

    if user.uid != chatroom.creator_uid:
        http_raise_forbidden(reason="User is not chatroom creator.")
    if moderators_count >= max_chatroom_moderators:
        http_raise_unprocessable_entity(
            reason=f"Unable to add user to moderators. max number of moderators allowed is {max_chatroom_moderators}."
        )
    if not candidate_is_member:
        http_raise_forbidden(
            reason=f"This candidate is not a member of the chatroom and cannot be made into a moderator."
        )
    if candidate_is_moderator:
        http_raise_unprocessable_entity(reason="User is already a moderator.")

    await add_chatroom_user_moderator_rel(user=candidate, chatroom=chatroom, db=db)
    await create_announcement_in_chat(
        message_content=f"@{candidate.username} is now an admin",
        chatroom=chatroom,
        db=db,
    )

    response = {"message": "Successfully added user to chatroom moderators."}
    return response


async def remove_user_from_chatroom_moderators(
    id: UUID, candidate_uid: UUID, user: User, db: AsyncSession, r_client: redis.Redis
) -> MessageResponse:
    """
    Remove `User` from `Chatroom` moderators.

    Args:
        id: UUID to retrieve matching `Chatroom`
        user: Logged in `User` instance
        db: Asynchronous database connection instance
        candidate_uid: UUID for `User` to be removed from `Chatroom` moderators

    Raises:
        HTTPException:
            403:
                -Logged in `User` is not `Chatroom`'s creator
            404:
                -No `Chatroom` with matching `id` exists
                -No `User` with matching `candidate_uid` exists
            422:
                -`Chatroom` is `public`
                -Candidite is not a moderator of `Chatroom`
    """
    chatroom = await get_chatroom(
        chatroom_identifier=id,
        use_case="remove moderator",
        from_cache=False,
        db=db,
        r_client=r_client,
    )
    await disallow_action_for_public_chatroom(chatroom=chatroom)

    if user.uid != chatroom.creator_uid:
        http_raise_forbidden(reason="User is not the chatroom creator")

    candidate = await get_user_by_uid(id=candidate_uid, db=db)
    candidate_is_moderator = await check_chatroom_user_moderator_rel(
        user=candidate, chatroom=chatroom, db=db
    )

    logger.info(f"removing user: {candidate.uid} from chatroom: {chatroom.uid}")

    if candidate.uid == chatroom.creator_successor_uid:
        chatroom.creator_successor_uid = None
        db.add(chatroom)

    if not candidate_is_moderator:
        http_raise_unprocessable_entity(reason="Candidate is not a moderator.")
    await remove_chatroom_user_moderator_rel(user=candidate, chatroom=chatroom, db=db)

    await db.commit()
    await db.refresh(chatroom)

    await set_chatroom_cache(chatroom=chatroom, r_client=r_client)
    response = {"message": "User successfully removed from chatroom moderators."}
    return response


async def assign_chatroom_successor(
    user: User, candidate_uid: UUID, id: UUID, db: AsyncSession, r_client: redis.Redis
) -> MessageResponse:
    """
    Assign `User` to become `Chatroom`'s successor.

    Args:
        id: UUID to retrieve matching `Chatroom`
        candidate_uid: UUID for candidate `User` to be assigned as `Chatroom` successor
        user: Logged in `User` instance
        db: Asynchronous database connection instance

        Raises:
        HTTPException:
            403:
                -Logged in `User` is not `Chatroom`'s creator
            404:
                -No `Chatroom` with matching `id` exists
                -No `User` with matching `candidate_uid` exists
            422:
                -`Chatroom` is `public`
                -Candidite is not a member of `Chatroom`
                -Candidite is not a moderator of `Chatroom`
                -Candidate is already `Chatroom`'s successor

    """
    chatroom = await get_chatroom(
        chatroom_identifier=id,
        use_case="assign successor",
        from_cache=False,
        db=db,
        r_client=r_client,
    )
    await disallow_action_for_public_chatroom(chatroom=chatroom)

    # check if user is the chatroom creeator
    # raise error if user is not creator
    if user.uid != chatroom.creator_uid:
        http_raise_forbidden(reason="User is not chatroom creator.")

    # check if creator is the same as candidate
    # raise error if creator is the same as successor candidate. successor cannot be creator
    candidate = await get_user_by_uid(id=candidate_uid, db=db)

    logger.info(
        f"assigning user: {candidate.uid} as the successor of chatroom: {chatroom.uid}"
    )

    # check if user is a member
    candidate_is_member = await check_chatroom_user_member_rel(
        user=candidate, chatroom=chatroom, db=db
    )
    # check if user is a moderator
    candidate_is_moderator = await check_chatroom_user_moderator_rel(
        user=candidate, chatroom=chatroom, db=db
    )

    if user.uid == candidate.uid:
        http_raise_forbidden(
            reason="Chatroom creator cannot be the chatroom successor."
        )
    if not candidate_is_member:
        http_raise_forbidden(
            reason="Candidate cannot be made into successor. Must first become a member of this chatroom."
        )
    if not candidate_is_moderator:
        http_raise_forbidden(
            reason="Candidate cannot be made into successor. Must first become a moderator of this chatroom."
        )

    if chatroom.creator_successor_uid == candidate.uid:
        http_raise_unprocessable_entity(
            reason="User is already the successor to this chatroom."
        )

    # set successor to candidate
    chatroom.creator_successor_uid = candidate.uid
    db.add(chatroom)
    await db.commit()
    await db.refresh(chatroom)

    logger.info(
        f"successfully assigned user: {candidate.uid} as successor of chatroom: {chatroom.uid}"
    )

    await set_chatroom_cache(chatroom=chatroom, r_client=r_client)
    return {"message": "Successfully made user into the successor."}


async def get_user_joined_chatrooms(
    user: User,
    page: int,
    db: AsyncSession,
    room_type: ChatroomPrivatePublicType,
    role: ChatroomMemberRole,
    sort: ChatroomsSort,
    order: SortOrder,
    search_query: str | None,
) -> RawChatroomList:
    """
    Returns all `Chatroom`s where logged in `User` is a member.

    Args:
        id: UUID to retrieve matching `Chatroom`
        user: Logged in `User` instance
        db: Asynchronous database connection instance
        room_type: determines type of `Chatroom`s to return e.g "private", "public"
        role: determines `Chatroom`s to return based on the logged in `User`'s role
        search_query: *optional* string used to find `Chatroom` with matching name or creator username
        :***
    """

    limit = 14
    offset = offset_by_page(page_num=page, limit=limit)

    query = (
        select(Chatroom)
        .where(Chatroom.room_type != "personal")
        .limit(limit)
        .offset(offset)
    )

    if role == ChatroomMemberRole.MODERATOR:
        query = query.join(UserChatroomModeratorsLink).where(
            UserChatroomModeratorsLink.user_uid == user.uid
        )
    elif role == ChatroomMemberRole.REMOVED:
        query = query.join(UserChatroomBannedLink).where(
            UserChatroomBannedLink.user_uid == user.uid
        )
    elif role == ChatroomMemberRole.CREATOR:
        query = query.where(Chatroom.creator_uid == user.uid)
    else:
        query = query.join(UserChatroomLink).where(
            UserChatroomLink.user_uid == user.uid
        )

    if room_type != ChatroomPrivatePublicType.ALL:
        query = query.where(Chatroom.room_type == room_type)

    if sort == ChatroomsSort.POPULARITY:
        query = (
            query.order_by(Chatroom.members_count.asc(), Chatroom.name.asc())
            if order == SortOrder.ASC
            else query.order_by(Chatroom.members_count.desc(), Chatroom.name.asc())
        )
    if sort == ChatroomsSort.NAME:
        query = (
            query.order_by(Chatroom.name.desc())
            if order == SortOrder.DESC
            else query.order_by(Chatroom.name.asc())
        )
    if sort == ChatroomsSort.DATE:
        query = (
            query.order_by(Chatroom.created_at.asc())
            if order == SortOrder.ASC
            else query.order_by(Chatroom.created_at.desc())
        )
    if sort == ChatroomsSort.ACTIVITY:
        query = (
            query.order_by(Chatroom.modified_at.asc(), Chatroom.name.asc())
            if order == SortOrder.ASC
            else query.order_by(Chatroom.modified_at.desc(), Chatroom.name.desc())
        )
    if search_query:
        search_query = unquote(search_query)
        search_query_first_string = search_query.split(" ")[0]
        query = query.where(
            or_(
                Chatroom.name.ilike(f"%{search_query}%"),
                Chatroom.original_creator_username.ilike(
                    f"%{search_query_first_string}%"
                ),
            )
        )

    executed_query = await db.execute(query)
    chatrooms = executed_query.unique().scalars().all()

    return {"chatrooms": chatrooms}


async def get_user_friends_with_active_chats(
    user: User, page: int, db: AsyncSession
) -> RawUserList:
    """
    Returns logged in `User`'s chats with friends.

    Args:
        user: Logged in `User` instance
        db: Asynchronous database connection instance
        :***
    """
    limit = 14
    offset = offset_by_page(page_num=page, limit=limit)

    user_chatroom_link_one = aliased(UserChatroomLink)
    user_chatroom_link_two = aliased(UserChatroomLink)
    query = (
        select(User, Chatroom)
        .join(user_chatroom_link_two, user_chatroom_link_two.user_uid == User.uid)
        .join(
            user_chatroom_link_one,
            user_chatroom_link_one.chatroom_uid == user_chatroom_link_two.chatroom_uid,
        )
        .where(user_chatroom_link_one.user_uid == user.uid)
        .where(User.uid != user.uid)
        .join(Chatroom)
        .where(Chatroom.room_type == "personal")
        .order_by(Chatroom.modified_at.desc())
        .limit(limit)
        .distinct()
        .offset(offset)
    )
    executed_query = await db.execute(query)
    users = executed_query.unique().scalars().all()

    logger.info(f"found {len(users)} matching friend chats for user {user.uid}")
    response = {"users": users}
    return response
