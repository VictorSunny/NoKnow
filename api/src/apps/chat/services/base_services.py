import datetime
import json
from typing import List
from urllib.parse import unquote
from uuid import UUID

from fastapi import WebSocketException
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy import delete, or_, func

import redis.asyncio as redis

from src.caching.services.redis_chatroom_caching import (
    clear_chatroom_cache,
    activate_chatroom_secret_mode,
    check_chatroom_secret_mode_active,
    clear_chatroom_cache,
    deactivate_chatroom_secret_mode,
    get_chatroom_from_cache,
    set_chatroom_cache,
)
from src.apps.chat.services.model_services import (
    add_chatroom_user_member_rel,
    add_chatroom_user_moderator_rel,
    check_chatroom_user_member_rel,
    check_chatroom_user_moderator_rel,
)
from src.generics.schemas import MessageResponse
from src.apps.user.schemas.base_schemas import UserRoleChoices
from src.apps.user.services.base_services import (
    check_friend_rel,
    get_user_by_username,
)
from src.utilities.utilities import (
    check_password,
    hash_password,
    is_uuid,
    offset_by_page,
    validate_uid_list,
)
from src.apps.chat.schemas.base_schemas import (
    ChatroomCreateForm,
    ChatroomDetails,
    ChatroomDetailsExtended,
    ChatroomDetailsExtendedList,
    ChatroomUserStatus,
    ChatroomPrivatePublicType,
    ChatroomType,
    ChatroomUpdate,
    ChatroomUser,
    MessageRead,
    MessagesList,
    RawChatroomList,
)
from src.db.models import Chatroom, Message, User, UserChatroomLink
from src.exceptions.http_exceptions import (
    http_raise_forbidden,
    http_raise_not_found,
    http_raise_unauthorized,
    http_raise_unprocessable_entity,
)
from src.services.websocket_manager import ws_manager

from logging import getLogger

logger = getLogger(__name__)


# UTILITY SERVICES FOR CHATROOM OPERATIONS


async def create_announcement_in_chat(
    message_content: str,
    chatroom: Chatroom,
    db: AsyncSession,
) -> MessageResponse:
    """
    Send announcement `Message` to `Chatroom`.

    Args:
        message_content: text body for `Message` to be sent
        chatroom: `Chatroom` instance to receive `Message`
        db: Asynchronous database connection instance
    """

    new_message = Message(
        type="announcement",
        content=message_content,
        content_type="text",
        chatroom_uid=chatroom.uid,
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)

    new_message_message = MessageRead(**new_message.model_dump())
    new_message_message.recorded = True
    new_message_message = json.loads(new_message_message.model_dump_json())
    await ws_manager.broadcast(message_json=new_message_message, id=chatroom.uid)

    return {"message": "Done."}


async def disallow_action_for_public_chatroom(chatroom: Chatroom):
    """
    Raises error if `Chatroom` is "public".
    """

    if chatroom.room_type == ChatroomPrivatePublicType.PUBLIC:
        http_raise_unprocessable_entity(
            reason="chatroom is public. action not allowed."
        )
    return


async def create_chatroom(
    json: ChatroomCreateForm,
    anon_username: str,
    db: AsyncSession,
    r_client: redis.Redis,
    user: User | None = None,
):
    """
    Create a new chatroom.

    Args:
        json: Creation form
        anon_username: string username used to identify user creating `Chatroom`
        db: Asynchronous database connection instance
        user: *optional* logged in `User` instance

    Raises:
        HTTPException:
            401: `Chatroom` is of type "private" and `User` is not logged in
            422:
                -`Chatroom` is "public" and "password" value was provided in creation `json`
                -`Chatroom` is "private" and no "password" value was provided in creation `json`
    """

    chatroom_is_private = json.room_type == ChatroomPrivatePublicType.PRIVATE

    original_creator_username = (
        user.username
        if (user) and (chatroom_is_private or not user.is_hidden)
        else anon_username
    )

    logger.info(
        f"creating {json.room_type} chatroom for user with username: {original_creator_username}"
    )
    if chatroom_is_private:
        if not user:
            http_raise_unauthorized(
                "User must be logged in to create a private chatroom."
            )

    new_chat = Chatroom(**json.model_dump(exclude={"confirm_password"}))
    new_chat.original_creator_username = original_creator_username.lower()
    if json.password:
        new_chat.password = hash_password(password=json.password)

    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat)

    if user:
        new_chat.creator_uid = user.uid
        await add_chatroom_user_member_rel(
            user=user, chatroom=new_chat, db=db, r_client=r_client
        )
    if chatroom_is_private:
        await add_chatroom_user_moderator_rel(user=user, chatroom=new_chat, db=db)

    logger.info(
        f"successfully created chatroom: {new_chat.uid} for user with username: {original_creator_username}. chatroom is {json.room_type}"
    )

    await create_announcement_in_chat(
        message_content=f"chatroom created by @{original_creator_username}",
        chatroom=new_chat,
        db=db,
    )

    await db.commit()
    return new_chat


async def update_chatroom_data(
    id: UUID,
    json: ChatroomUpdate,
    user: User,
    db: AsyncSession,
    r_client: redis.Redis,
    is_admin_action: bool | None = False,
) -> Chatroom:
    """
    Changes `Chatroom` field values.

    Args:
        id: UUID for `Chatroom` to be updated
        json: Update form
        user: Logged in `User` instance
        db: Asynchronous database connection instance
        r_client: Redis client instance

    Raises:
        HTTPExcpetion:
            403:
                -Logged in `User` is not the creator of `Chatroom`
            404: `Chatroom` does not exist
            422:
                -`Chatroom` is "public" and "password" value was provided in creation `json`
                -`Chatroom` is "private" and no "password" value was provided in creation `json`
    """

    chatroom = await get_chatroom(
        chatroom_identifier=id,
        use_case="data update",
        from_cache=False,
        db=db,
        r_client=r_client,
    )

    # raise error if chatroom is not found
    if not chatroom:
        http_raise_not_found(reason="Chatroom does not exist.")
    # raise error if user is not the chatrooom creator, and this function is not being used in an admin context
    if (user.uid != chatroom.creator_uid) and (not is_admin_action):
        http_raise_forbidden(reason="Only chatroom creator can update details")

    # raise error if user tries to add password to chatroom that is not of type "private"
    if (chatroom.room_type != ChatroomType.PRIVATE) and (json.password):
        http_raise_unprocessable_entity(
            reason="Only a private chatroom can be password protected."
        )

    logger.info(f"updating data for chatroom: {chatroom.uid}")
    # raise error if no change is detected
    if chatroom.name == json.name:
        if chatroom.about == json.about:
            if not json.password:
                http_raise_unprocessable_entity(reason="No changes detected.")
            if chatroom.password:
                password_matches = check_password(
                    password=json.password, hashed_password=chatroom.password
                )
                if password_matches:
                    http_raise_unprocessable_entity(reason="No changes detected.")

    # parse password if provided
    if json.password:
        if (user.uid != chatroom.creator_uid) and (
            user.role != UserRoleChoices.SUPERUSER
        ):
            http_raise_forbidden(
                "User does not have permission to update chatroom password."
            )
        json.password = hash_password(password=json.password)

    # remove fields with `None` value
    json = json.model_dump(exclude_unset=True, exclude={"confirm_password"})
    if not json:
        http_raise_unprocessable_entity(reason="Please fill at least one field.")

    await clear_chatroom_cache(id=chatroom.uid, r_client=r_client)
    # update model instance fields
    for key, value in json.items():
        # update model field if value is not an empty string
        if hasattr(chatroom, key) and (not str(value).strip() == ""):
            setattr(chatroom, key, value)

    db.add(chatroom)
    await db.commit()
    await db.refresh(chatroom)
    await set_chatroom_cache(chatroom=chatroom, r_client=r_client)
    logger.info(f"successfully updated data for chatroom: {chatroom.uid}")
    return chatroom


async def get_create_friend_chatroom(
    user: User | None,
    candidate_username: str,
    db: AsyncSession,
    r_client: redis.Redis,
    websocket_conn: bool | None = False,
    create_new: bool | None = True,
) -> Chatroom:
    """
    Retrieves and/or creates new `Chatroom` for logged in `User` and second `User` witb matching `candidate_username`.

    Args:
        user: *optional* Logged in `User` instance
        candidate_username: string for second `User` to be added to `Chatroom`
        db: Asynchronous database connection instance
        wbesocket_conn: value indicating to function is being used within a `WebSocket` context
            used for throwing relevant error. if "True", errors are thrown as WebSocketExcpetion`s instead of `HTTPException`s
        create_new: value indicating whether to create a new `Chatroom` in case no match for `user` and candidate is found.

    Raises:
        HTTPException:
            401: no `user` value was passed
            403: Logged in `User` is not a friend to `User` with matching `candidate_username`
            404:
                -`Chatroom` does not exists and `create_new` is `False`
                -`User` with matching `candidate_username` does not exist
            422: Logged in `User` tries to connect to chat with self

        WebSocketException:
            401: no `user` value was passed
            403: Logged in `User` is not a friend to `User` with matching `candidate_username`
            404:
                -`Chatroom` does not exists and `create_new` is `False`
                -`User` with matching `candidate_username` does not exist
            422: Logged in `User` tries to connect to chat with self
    """

    if not user:
        if websocket_conn:
            raise WebSocketException(401, "User is not logged in")
        http_raise_unauthorized("User is not logged in.")

    if user.username == candidate_username:
        if websocket_conn:
            raise WebSocketException(442, "User cannot chat with self.")
        http_raise_unprocessable_entity("User cannot chat with self.")

    candidate = await get_user_by_username(
        username=candidate_username,
        websocket_conn=websocket_conn,
        db=db,
        r_client=r_client,
    )

    # check if user is friends with candidate
    candidate_is_friend = await check_friend_rel(user=user, to_check=candidate, db=db)

    logger.info(
        f"retrieving personal chatroom messages for users: {user.uid} and {candidate.uid}"
    )

    if not candidate_is_friend:
        if websocket_conn:
            raise WebSocketException(
                403, "User is not a friend and cannot be engaged in a chat."
            )
        http_raise_forbidden("User is not a friend and cannot be engageg in a chat.")

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

    if not friend_chatroom:
        # raise error if new chatroom is not to be created, else create new chatroom for return
        if not create_new:
            if websocket_conn:
                raise WebSocketException(404, "No chat exists with this user.")
            http_raise_not_found("No chat exists with this user.")

        logger.info(f"no chat exists between users {user.uid} and {candidate.uid}")
        chatroom_name = (f"{user.username}-{candidate.username}")[:64]

        new_friend_chat = Chatroom(
            name=chatroom_name,
            original_creator_username=user.username,
            room_type=ChatroomType.PERSONAL,
            about=f"${user.uid}-{candidate.uid}",
        )

        await add_chatroom_user_member_rel(
            user=user, chatroom=new_friend_chat, db=db, r_client=r_client
        )
        await add_chatroom_user_member_rel(
            user=candidate, chatroom=new_friend_chat, db=db, r_client=r_client
        )

        await db.commit()
        await db.refresh(new_friend_chat)

        # set friend chatroom from none to new_friend_chat
        friend_chatroom = new_friend_chat

        await create_announcement_in_chat(
            message_content=f"{user.username} started the chat.",
            chatroom=new_friend_chat,
            db=db,
        )
    logger.info(f"found friend chatroom: {friend_chatroom.name}")

    return friend_chatroom


async def get_chatroom_extended_details(
    user: User | None, chatroom_identifier: str, db: AsyncSession, r_client: redis.Redis
):
    chatroom: Chatroom = await get_chatroom(
        chatroom_identifier=chatroom_identifier,
        use_case="retrieve extended details",
        user=user,
        create_new=False,
        db=db,
        r_client=r_client,
    )
    secret_mode_active = await check_chatroom_secret_mode_active(
        id=chatroom.uid, r_client=r_client
    )
    chatroom_details = ChatroomDetailsExtended(**chatroom.model_dump())
    chatroom_details.active_visitors = await ws_manager.get_chatroom_active_users(
        id=chatroom.uid
    )
    chatroom_details.secret_mode = secret_mode_active
    if user:
        chatroom_details.user_is_hidden = user.is_hidden
        # check if user is a member
        user_is_member = await check_chatroom_user_member_rel(
            user=user, chatroom=chatroom, db=db
        )
        # check if user is a moderator
        user_is_moderator = await check_chatroom_user_moderator_rel(
            user=user, chatroom=chatroom, db=db
        )

        if user.uid == chatroom.creator_uid:
            chatroom_details.user_status = ChatroomUserStatus.CREATOR
        elif user_is_moderator:
            chatroom_details.user_status = ChatroomUserStatus.MODERATOR
        elif user_is_member:
            chatroom_details.user_status = ChatroomUserStatus.MEMBER
        else:
            chatroom_details.user_status = ChatroomUserStatus.REMOVED
    else:
        chatroom_details.user_status = ChatroomUserStatus.REMOVED

    return chatroom_details


async def get_chatroom(
    chatroom_identifier: str,
    use_case: str,
    db: AsyncSession,
    r_client: redis.Redis,
    user: User | None = None,
    websocket_conn: bool | None = False,
    create_new: bool | None = True,
    from_cache: bool | None = True,
) -> Chatroom:
    """
    Returns `Chatroom`.

    Args:
        chatroom_identifier: string or UUID value for retriving `Chatroom`
        user: *optional* logged in `User` instance
        db: Asynchronous database connection instance
        r_client: Redis client instance
        use_case: Reason for retrieving `Chatroom`(used for logging)
        wbesocket_conn: value indicating to function is being used within a `WebSocket` context
            used for throwing relevant error. if "True", errors are thrown as WebSocketExcpetion`s instead of `HTTPException`s

    Raises:
        HTTPException:
            401: no `user` value was passed and `Chatroom` is protected
            403: Logged in `User` is restricted from retrieving `Chatroom`.
                see `get_create_friend_chatroom` fn for possible reasons)
            404:
                -`Chatroom` does not exists

        WebSocketException:
            401: no `user` value was passed and `Chatroom` is protected
            403: Logged in `User` is restricted from retrieving `Chatroom`.
                see `get_create_friend_chatroom` fn for possible reasons)
            404:
                -`Chatroom` does not exists

    """
    chatroom = None
    cached_chatroom = None

    if from_cache:
        cached_chatroom = await get_chatroom_from_cache(
            chatroom_identifier=chatroom_identifier,
            r_client=r_client,
        )
        if cached_chatroom:
            chatroom = cached_chatroom
    # retrieve chatroom from database if it does not exist in cache
    if not chatroom:
        chatroom_identifier = str(chatroom_identifier)
        identifier_is_uuid = is_uuid(uuid_str=chatroom_identifier)
        if identifier_is_uuid:
            chatroom_identifier = UUID(chatroom_identifier)
            chatroom = await db.get(Chatroom, chatroom_identifier)
        elif type(chatroom_identifier) == str:
            chatroom = await get_create_friend_chatroom(
                user=user,
                candidate_username=chatroom_identifier,
                db=db,
                websocket_conn=websocket_conn,
                create_new=create_new,
            )

    # raise error if chatroom does not exist
    if not chatroom:
        if not websocket_conn:
            http_raise_not_found(reason="Chatroom does not exist.")
        raise WebSocketException(404, "Chatroom does not exist.")

    # store chatroom in cache
    if not cached_chatroom:
        await set_chatroom_cache(
            chatroom=chatroom,
            r_client=r_client,
        )

    logger.info(f"retrieved chatroom: {chatroom.uid} to {use_case}")
    return chatroom


# INTEGRATED SERVICES FOR CHATROOM OPERATIONS
async def get_chatroom_messages(
    chatroom_identifier: UUID | str,
    earliest_date: datetime.datetime,
    # offset: int,
    user: User | None,
    db: AsyncSession,
    r_client: redis.Redis,
) -> MessagesList:
    """
    Returns dictionary with `Message`s for `Chatroom`.

    Args:
        chatroom_identifier: string or UUID value for retriving `Chatroom`
        offset: number of `Message` rows to skip
        db: Asynchronous database connection instance
        user: *optional* logged in `User` instance

    Raises:
        HTTPException:
            401: `Chatroom` is protected and no `user` value was provided
            403: `Chatroom` is protected and logged in `User` is not a member
    """
    # "offset" parameter will be used to handle pagination instead of "page"...
    # due to messages being added in realtime. fetching by pages would fetch duplicate messages
    # on the front-end, offset will be calculated by the length(int) of the current list of messages present in the UI

    chatroom = await get_chatroom(
        chatroom_identifier=chatroom_identifier,
        use_case="retrieve messages",
        db=db,
        user=user,
        r_client=r_client,
    )
    chatroom_uid = chatroom.uid

    logger.info(f"retrieiving messages for chatroom: {chatroom_uid}")

    # check if chat is private
    if chatroom.room_type != ChatroomType.PUBLIC:
        if not user:
            http_raise_unauthorized(
                reason="Chatroom is not public. Please login and retry."
            )
        user_is_member = await check_chatroom_user_member_rel(
            user=user, chatroom=chatroom, db=db
        )
        if not user_is_member:
            http_raise_forbidden(reason="User is not a member of this chatroom.")

    limit = 24
    query = (
        select(Message)
        .where(Message.chatroom_uid == chatroom_uid)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    if (earliest_date) and (not str(earliest_date).isnumeric()):
        timestamp = earliest_date.timestamp()
        query = query.where(Message.created_at < timestamp)

    db_response = await db.execute(query)
    messages = db_response.scalars().all()

    logger.info(f"successfully retrieved messages for chatroom: {chatroom_uid}")

    messages_detail = {
        "room_type": chatroom.room_type,
        "messages": reversed(messages),
    }
    return messages_detail


async def search_chatrooms(
    search_query: str,
    page: int,
    db: AsyncSession,
    room_type: ChatroomPrivatePublicType | None,
) -> List[ChatroomDetails]:
    """
    Returns `Chatroom`s matching search keyword.

    Args:
        search_query: string value used to find matching `Chatroom`s
        db: Asynchronous database connection instance
        room_type: the type of `Chatroom`s to return e.g "private", "public"
        :***
    """

    search_query = unquote(search_query)
    logger.info(f"searching database for chatrooms matching query: {search_query}")

    limit = 14
    offset = offset_by_page(page_num=page, limit=limit)

    query = (
        select(Chatroom)
        .limit(limit)
        .offset(offset)
        .where(Chatroom.room_type != "personal")
        .order_by(Chatroom.modified_at.desc())
    )
    # incase search query is creator username get first word in string
    search_query_first_string = search_query.split(" ")[0]
    query = query.where(
        or_(
            Chatroom.name.ilike(f"%{search_query}%"),
            Chatroom.original_creator_username.ilike(f"%{search_query_first_string}%"),
        )
    )

    if room_type and (room_type != ChatroomPrivatePublicType.ALL):
        query = query.where(Chatroom.room_type == room_type)

    excuted_query = await db.execute(query)
    all_chatrooms = excuted_query.unique().scalars().all()

    logger.info(
        f"found {len(all_chatrooms)} matching chatroom(s) for search: {search_query}"
    )

    response = {"chatrooms": all_chatrooms}
    return response


async def get_chatrooms_info_by_uids(
    id_list_string: str, db: AsyncSession, limit: int = 8
) -> RawChatroomList:
    """
    Returns `Chatroom`s with matching IDs. Number of chatrooms retrieved is limited.

    Args:
        id_list_string: Comma seperated list of ids to find `Chatroom`s
        db: Asynchronous database connection instance
        user: *optional* Logged in `User`
        limit: Maximum number of table rows to retrieve

    Raises:
        HTTPException 404: Not a single matching `Chatroom1 exists
    """

    # extract valid uids from id string
    chatrooms_uid_list = await validate_uid_list(
        model_name="chatroom", uid_list=id_list_string, safe=True
    )

    logger.info(f"retrieving chatrooms with matching UIDs: {chatrooms_uid_list}")
    query = (
        select(Chatroom)
        .where(Chatroom.uid.in_(chatrooms_uid_list))
        .where(Chatroom.room_type != "personal")
        .order_by(Chatroom.modified_at.desc())
        .limit(limit)
    )

    excuted_query = await db.execute(query)
    all_chatrooms = excuted_query.unique().scalars().all()

    if len(all_chatrooms) < 1:
        http_raise_not_found(reason="No matching chatroom found.")

    logger.info(f"found {len(all_chatrooms)} matching chatroom(s)")

    response = {"chatrooms": all_chatrooms}

    return response


async def get_user_with_chatroom_role(
    id: UUID,
    username: str | None,
    user: User | None,
    db: AsyncSession,
    r_client: redis.Redis,
) -> ChatroomUser:
    """
    Returns `User` details with `User`'s role in `Chatroom`.

    Args:
        id: UUID for matching `Chatroom`
        user: Logged in `User` instance
        username: *optional* String value for `User` details to return.
            If not provided, returns logged in `User`'s instead
        db: Asynchronous database connection instance

    Raises:
        HTTPException:
            401: No `user` nor `username` values were provided
            404: `Chatroom` does not exist
    """

    if not user and not username:
        http_raise_unauthorized(
            "User is not logged in and no username parameter provided."
        )

    # if no username is provided, set username for query to logged in user's username
    # else continue with provided username regardless that user is logged in
    if username:
        user = await get_user_by_username(username=username, db=db, r_client=r_client)

    chatroom = await get_chatroom(
        chatroom_identifier=id, use_case="check user role", db=db, r_client=r_client
    )

    user_details = ChatroomUser(**user.model_dump())

    # check if user is a member
    user_is_member = await check_chatroom_user_member_rel(
        user=user, chatroom=chatroom, db=db
    )
    # check if user is a moderator
    user_is_moderator = await check_chatroom_user_moderator_rel(
        user=user, chatroom=chatroom, db=db
    )

    if user.uid == chatroom.creator_uid:
        user_details.user_status = ChatroomUserStatus.CREATOR
    elif user.uid == chatroom.creator_successor_uid:
        user_details.user_status = ChatroomUserStatus.SUCCESSOR
    elif user_is_moderator:
        user_details.user_status = ChatroomUserStatus.MODERATOR
    elif user_is_member:
        user_details.user_status = ChatroomUserStatus.MEMBER
    else:
        user_details.user_status = ChatroomUserStatus.REMOVED

    return user_details


async def get_chatroom_secrecy_status(id: UUID, redis: redis.Redis):

    pass


async def toggle_chatroom_recording_status(
    id: UUID, user: User, db: AsyncSession, r_client: redis.Redis
) -> MessageResponse:
    """
    Toggles `Chatroom` recording status, allowing `Messages` sent to `Chatroom` websocket connections to either be saved or not,
    Adding extra privacy to `Chatroom` if toggled on.

    Args:
        id: UUID for `Chatroom`
        user: Logged in `User` instance
        db: Asynchronous database connection instance
        r_client: Redis client instance
    Raises:
        403:
            -Logged in `User` is not a moderator of `Chatroom`
            -Logged in `User` is not a member of `Chatroom`
        404: `Chatroom` does not exist
        422: `Chatroom` is of type "public"

    """

    chatroom = await get_chatroom(
        chatroom_identifier=id,
        use_case="reset unrecorded status",
        db=db,
        r_client=r_client,
    )

    await disallow_action_for_public_chatroom(chatroom=chatroom)

    # check if user is a moderator
    user_is_moderator = await check_chatroom_user_moderator_rel(
        user=user, chatroom=chatroom, db=db
    )
    user_is_member = await check_chatroom_user_member_rel(
        user=user, chatroom=chatroom, db=db
    )

    # raise error if chatroom is not a friend conversation
    if (
        (chatroom.room_type != ChatroomType.PERSONAL)
        and (not user_is_moderator)
        and (user.uid != chatroom.creator_uid)
    ):
        http_raise_forbidden(reason="User is not a moderator.")

    if not user_is_member:
        http_raise_forbidden(reason="User is not a member of this chat.")

    secret_mode_active = await check_chatroom_secret_mode_active(
        id=chatroom.uid, r_client=r_client
    )
    if secret_mode_active:
        await deactivate_chatroom_secret_mode(id=chatroom.uid, r_client=r_client)
    else:
        await activate_chatroom_secret_mode(id=chatroom.uid, r_client=r_client)

    return {
        "message": f"Successfully switched chat messages recording status to {not secret_mode_active}"
    }


async def get_currently_active_public_chatrooms(db: AsyncSession) -> RawChatroomList:
    """
    Returns `Chatroom`s with active `WebSocket` connections.

    Args:
        db: Asynchronous database connection instance
    """
    chatrooms_uid_list = ws_manager.get_active_chatrooms()
    query = (
        select(Chatroom)
        .where(Chatroom.uid.in_(chatrooms_uid_list))
        .where(Chatroom.room_type == ChatroomPrivatePublicType.PUBLIC)
        .order_by(Chatroom.modified_at.desc())
        .limit(10)
    )
    excuted_query = await db.execute(query)
    chatrooms = excuted_query.unique().scalars().all()

    return {"chatrooms": chatrooms}


async def delete_chatroom(
    id: UUID, user: User, db: AsyncSession, r_client: redis.Redis
) -> MessageResponse:
    """
    Deletes chatroom.

    Args:
        id: UUID for `Chatroom`
        user: Logged in `User` instance
        db: Asynchronous database connection instance
    """
    chatroom = await get_chatroom(
        chatroom_identifier=id,
        use_case="delete",
        db=db,
        r_client=r_client,
        from_cache=False,
    )

    # confirm user is chatroom creator
    if (chatroom.room_type != ChatroomType.PERSONAL) and (
        user.uid != chatroom.creator_uid
    ):
        http_raise_forbidden(reason="Chatroom can only be deleted by it's creator.")

    # confirm user is a member of chatroom
    user_is_member = await check_chatroom_user_member_rel(
        user=user, chatroom=chatroom, db=db
    )
    if not user_is_member:
        http_raise_forbidden(
            reason="Chatroom cannot be deleted as user is not a member."
        )

    # delete chatroom
    await clear_chatroom_cache(id=chatroom.uid, r_client=r_client)
    query = delete(Chatroom).where(Chatroom.uid == chatroom.uid)
    await db.execute(query)
    await db.commit()

    return {"message": "Success."}
