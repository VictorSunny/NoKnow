from uuid import UUID
import json
from uuid import UUID
from fastapi import WebSocket, WebSocketDisconnect, WebSocketException

from src.utilities.utilities import timestamp_now
from src.apps.chat.services.base_services import get_chatroom
from src.apps.auth.services.jwt_services import get_current_websocker_user
from src.apps.chat.schemas.base_schemas import (
    ChatroomType,
    MessageContentType,
    MessageReadCreate,
)

from src.db.database import async_session_maker
from src.db.models import Chatroom, Message

from src.apps.chat.schemas.base_schemas import MessageReadCreate

from src.apps.chat.services.websocket_manager import ws_manager

from logging import getLogger

logger = getLogger(__name__)


async def websocket_send_message(
    message_content: str,
    content_type: MessageContentType,
    id: UUID,
    sender_username: str,
    sender_uid: UUID | None,
    websocket: WebSocket,
) -> MessageReadCreate | None:
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
        blank_message_error_alert = MessageReadCreate(
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
    async with async_session_maker() as db:
        chatroom: Chatroom = await db.get(Chatroom, id)
        if not chatroom:
            raise WebSocketException(404, "Chatroom does not exist.")
        # update chatroom `last active` date
        chatroom.modified_at = timestamp_now()
        db.add(chatroom)

        # save message if chatroom allows recording
        if chatroom.record_messages:
            db.add(new_message)

        await db.commit()
        await db.flush()
        await db.close()

    message_details = MessageReadCreate.model_validate(new_message)
    message_details.recorded = chatroom.record_messages

    message = json.loads(message_details.model_dump_json())
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

    if token:
        # retrieve user if JWT `token` is valid
        try:
            user = await get_current_websocker_user(token=token)
        except Exception as e:
            logger.debug(f"get ws user error - ignore: {e}")
            user = None

    async with async_session_maker() as db:
        # get chatroom using identifier
        chatroom = await get_chatroom(
            chatroom_identifier=chatroom_identifier,
            use_case="connect to chatroom websocket",
            db=db,
            user=user,
            websocket_conn=True,
        )

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
            await ws_manager.connect(
                websocket=websocket, id=chatroom.uid, user=user, db=db
            )
            logger.info(
                f"user: {sender_username} connected successfully to chatroom: {chatroom.uid}"
            )
            entered_announcement_message = MessageReadCreate(
                type="info",
                content=f"@{sender_username} entered",
                content_type="text",
                recorded=False,
            ).model_dump_json()
            await ws_manager.broadcast(
                id=chatroom.uid,
                message_json=json.loads(entered_announcement_message),
            )
        except Exception as e:
            logger.error(f"websocket.connect error: {e}")
            raise e
        finally:
            await db.close()

    try:
        # keep websocket connected and open to sending & receiving text data
        while True:
            message_content = await websocket.receive_text()
            if message_content:
                try:
                    message_json = await websocket_send_message(
                        message_content=message_content,
                        content_type="text",
                        id=chatroom.uid,
                        sender_username=sender_username,
                        sender_uid=sender_uid,
                        websocket=websocket,
                    )
                    if message_json:
                        await ws_manager.broadcast(
                            id=chatroom.uid, message_json=message_json
                        )
                # alert connected websocket user of any unexpected error on message sending
                except WebSocketException as e:
                    error_reason, error_response_code = e.reason, e.code

                    error_message_json = MessageReadCreate(
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

        # set messages saving on when the last active user exits the chat
        current_active_users = ws_manager.get_chatroom_active_users(id=chatroom.uid)
        if current_active_users < 1:
            async with async_session_maker() as db:
                chatroom: Chatroom = await db.get(Chatroom, chatroom.uid)
                if not chatroom.record_messages:
                    chatroom.record_messages = True
                    db.add(chatroom)
                    await db.commit()

        # announce to chat that websocket user has left the chat
        left_announcement_message = MessageReadCreate(
            type="info",
            content=f"@{sender_username} left",
            content_type="text",
            recorded=False,
        ).model_dump_json()
        await ws_manager.broadcast(
            id=chatroom.uid,
            message_json=json.loads(left_announcement_message),
        )

    # raise and log any unexpected error in websocket connection lifespan
    except Exception as e:
        logger.debug(f"unexpected websocket error: {e}")
        raise WebSocketException(
            code=500, reason=f"unexpected server error handling websocket request: {e}"
        )
