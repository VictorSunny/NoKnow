from uuid import UUID
import json
from uuid import UUID
from fastapi import WebSocket, WebSocketDisconnect, WebSocketException

import redis.asyncio as redis

from src.configurations.config import Config
from src.caching.services.redis_chatroom_caching import (
    check_record_message,
    get_chatroom_from_cache,
    set_chatroom_modified_at_cache,
    set_chatroom_cache,
)
from src.apps.chat.services.base_services import get_chatroom
from src.apps.auth.services.jwt_services import get_current_websocker_user
from src.apps.chat.schemas.base_schemas import (
    ChatroomType,
    MessageContentType,
    MessageRead,
)

from src.db.database import async_session_maker
from src.db.models import Message

from src.apps.chat.schemas.base_schemas import MessageRead

from src.services.websocket_manager import ws_manager

from logging import getLogger

logger = getLogger(__name__)


async def websocket_send_message(
    message_content: str,
    content_type: MessageContentType,
    id: UUID,
    sender_username: str,
    sender_uid: UUID | None,
    websocket: WebSocket,
    r_client: redis.Redis,
) -> MessageRead | None:
    """
    Saves `Message` to database before returning if `Chatroom` allows messages to be recorded,
    then returns `Message` json.

    Alerts `Websocket` on error, then returns `None`

    Args:
        content_type: File type of message e.g "text", "image"
        message_content: Text body for `Message` to be sent
        id: UUID for `Chatroom` to send `Message` to
        sender_username: String username of sender
        sender_uid: *optional* id of message sender
        websocket: WebSocket instance

    """
    if (len(message_content) < 1) or (message_content.isspace()):
        blank_message_error_alert = MessageRead(
            type="alert",
            content="unable to send empty text",
            recorded=False,
            content_type="text",
        )
        message = json.loads(blank_message_error_alert.model_dump_json())
        await ws_manager.alert_current_websocket(
            message_json=message, websocket=websocket, response_code=422
        )
        return None

    content = message_content.strip()
    new_message = Message(
        type="user",
        content=content,
        content_type=content_type,
        sender_username=sender_username,
        sender_uid=sender_uid,
        chatroom_uid=id,
    )
    message_details = MessageRead.model_validate(new_message)

    record = await check_record_message(id=id, r_client=r_client)
    message_details.recorded = record

    message = json.loads(message_details.model_dump_json())
    # publish message to listening subscribers which will then broadcast to their connected websockets
    if record:
        message_to_queue = json.loads(new_message.model_dump_json(exclude_none=True))
        await r_client.lpush(Config.REDIS_MESSAGE_LIST, str(message_to_queue))
        await set_chatroom_modified_at_cache(id=id, r_client=r_client)

    await ws_manager.publish(id=id, message_content=message)
    return message


async def engage_chatroom_conversation(
    websocket: WebSocket,
    chatroom_identifier: UUID | str,
    anon_username: str,
    token: str | None = None,
):
    """
    Adds `Websocket` user to websocket connection of `Chatroom` allowing user to send and receive `Message`s.

    Args:
        websocket: `Websocket` instance
        chatroom_identifier: UUID or string for retrieving `Chatroom` to connect to
        anon_username: string username used to identify user in chat
        token: JWT string for user authorization when connecting to protected `Chatroom` websocket

    Raises:
        WebsocketException:
            401: `Chatroom` is protected and user is not logged/`token` invalid, or `token` not provided
            404: `Chatroom` with matching `chatroom_identifier` does not exist
            403: Logged in `User` is restricted from connecting to protected `Chatroom`
            422: Logged in `User` tries connecting to chat with self
            500: Unexpected server-side error

    """
    sender_username = anon_username
    logger.info(f"user: {sender_username} engaging chat")
    user = None
    sender_uid = None
    r_client = websocket.app.state.r_client
    if token:
        # retrieve user if JWT `token` is valid
        try:
            user = await get_current_websocker_user(token=token, r_client=r_client)
        except Exception as e:
            logger.debug(f"get ws user error - ignore: {e}")
            user = None

    chatroom = await get_chatroom_from_cache(
        chatroom_identifier=chatroom_identifier,
        r_client=r_client,
    )
    if not chatroom:
        async with async_session_maker() as db:
            # get chatroom using identifier
            chatroom = await get_chatroom(
                chatroom_identifier=chatroom_identifier,
                use_case="connect to chatroom websocket",
                db=db,
                r_client=r_client,
                user=user,
                websocket_conn=True,
            )
            await set_chatroom_cache(chatroom=chatroom, r_client=r_client)
    # set sender id if user is logged in
    if user:
        sender_uid = user.uid
        # set sender username to logged in user's username if user is not hidden
        if user.is_hidden and (chatroom.room_type != ChatroomType.PERSONAL):
            sender_username = anon_username
        else:
            sender_username = user.username

    # add websocket to chatroom websocket connection
    try:
        await ws_manager.connect(websocket=websocket, chatroom=chatroom, user=user)
        logger.info(
            f"user: {sender_username} connected successfully to chatroom: {chatroom.uid}"
        )
        entered_announcement_message = MessageRead(
            type="info",
            content=f"@{sender_username} entered",
            content_type="text",
            recorded=False,
        ).model_dump_json()
        message_content = json.loads(entered_announcement_message)
        await ws_manager.publish(id=chatroom.uid, message_content=message_content)
    except Exception as e:
        logger.error(f"websocket.connect error: {e}")
        raise e

    try:
        while True:
            message_content = await websocket.receive_text()
            if message_content:
                try:
                    await websocket_send_message(
                        message_content=message_content,
                        content_type="text",
                        id=chatroom.uid,
                        sender_username=sender_username,
                        sender_uid=sender_uid,
                        websocket=websocket,
                        r_client=r_client,
                    )
                # alert connected websocket user of any unexpected error on message sending
                except WebSocketException as e:
                    error_reason, error_response_code = e.reason, e.code
                    error_message_json = MessageRead(
                        type="alert",
                        content=error_reason,
                        content_type="text",
                        recorded=False,
                    ).model_dump_json()
                    error_message_json = json.loads(error_message_json)
                    await ws_manager.alert_current_websocket(
                        websocket=websocket,
                        message_json=error_message_json,
                        response_code=error_response_code,
                    )

    # gracefully remove websocket user from chatroom's active websocket connections upon user disconnection
    except WebSocketDisconnect:
        await ws_manager.disconnect(id=chatroom.uid, websocket=websocket)
        # announce to chat that websocket user has left the chat
        left_announcement_message = MessageRead(
            type="info",
            content=f"@{sender_username} left",
            content_type="text",
            recorded=False,
        ).model_dump_json()

        message_content = json.loads(left_announcement_message)
        await ws_manager.publish(id=chatroom.uid, message_content=message_content)

    # raise and log any unexpected error in websocket connection lifespan
    except Exception as e:
        logger.debug(f"unexpected websocket error: {e}")
        raise WebSocketException(
            code=500, reason=f"unexpected server error handling websocket request: {e}"
        )
