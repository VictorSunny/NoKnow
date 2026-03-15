from typing import Dict, List
from uuid import UUID
from fastapi import WebSocket, WebSocketException
from sqlalchemy import exists
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select

from src.apps.chat.schemas.base_schemas import ChatroomType, MessageReadCreate
from src.db.models import Chatroom, User, UserChatroomLink

from logging import getLogger

logger = getLogger(__name__)


class WebSocketManager:
    """
    `WebSocketManager` class handles `Chatroom` `WebSocket` connections.
    """

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    def get_active_chatrooms(self):
        """
        Returns 40(max) most recent chatrooms that are currently engaged with at least one user.
        """
        active_chatrooms = list(reversed(self.active_connections.keys()))[:50]
        return active_chatrooms

    def get_chatroom_active_users(self, id: UUID) -> int:
        """
        Returns total number of `WebSocket`s actively connected to `Chatroom` websocket connection

        Args:
            if: UUID for `Chatroom` to check
        """
        active_users = 0
        if id in self.active_connections:
            active_connections = self.active_connections[id]
            active_users = len(active_connections)
        return active_users

    async def connect(
        self, id: UUID, user: User, websocket: WebSocket, db: AsyncSession
    ):
        """
        Adds `WebSocket` to `Chatroom` websocket connections.

        Args:
            id: UUID for `Chatroom` to add `WebSocket`
            user: *optional* `User` instance
            websocker: `WebSocket` instance
            db: Asynchronous database connection instance
        """
        chatroom = await db.get(Chatroom, id)
        error_message_prefix = f"error connecting."

        # raise error if chatroom does not exist
        if not chatroom:
            raise WebSocketException(
                404, f"{error_message_prefix} Chatroom does not exist."
            )

        # if chatroom is not a public chatroom
        # raise necessary errors if user does not meet requirements for protected chatrooms
        if chatroom.room_type != ChatroomType.PUBLIC:
            if not user:
                raise WebSocketException(
                    401,
                    f"Chatroom is private and user is not logged in.",
                )

            query = select(
                exists().where(
                    UserChatroomLink.chatroom_uid == chatroom.uid,
                    UserChatroomLink.user_uid == user.uid,
                )
            )
            executed_query = await db.execute(query)
            user_is_member = executed_query.scalar_one_or_none()

            # check if user is a member
            if chatroom.room_type == ChatroomType.PRIVATE:
                if not user_is_member:
                    raise WebSocketException(
                        403,
                        f"{error_message_prefix} User is not a member of this chatroom.",
                    )
            if chatroom.room_type == ChatroomType.PERSONAL:
                if not user_is_member:
                    raise WebSocketException(
                        403, f"{error_message_prefix} User is not a friend."
                    )

        await websocket.accept()
        self.active_connections.setdefault(id, []).append(websocket)

    # confirm chatroom websocket connection for user to be disconnected from
    async def disconnect(self, id: UUID, websocket: WebSocket):
        """
        Removes `WebSocket` from `Chatroom` websocket connection.
        Closes `Chatroom` websocket connection if empty after `WebSocket` removal.

        Args:
            id: UUID for `Chatroom` websocket connection
            websocket: `WebSocket` instance

        """
        # delete websocket connection if in active_connections related to chatroom with matching uid
        if id in self.active_connections:
            self.active_connections[id].remove(websocket)
            logger.info(f"websocket: {websocket} disconnected chat: {id}")

            # delete chatroom websocket connection if empty
            if not self.active_connections[id]:
                del self.active_connections[id]
                logger.info(f"websocket connection for chat: {id} closed")

    async def alert_current_websocket(
        self, message_json: MessageReadCreate, websocket: WebSocket, response_code: int
    ):
        """
        Sends a warning message to a single `WebSocket`
        """
        message_json.update({"response_code": response_code})
        await websocket.send_json(message_json)

    # send message to all users in active websocket connection for chatroom
    async def broadcast(self, message_json: MessageReadCreate, id: UUID):
        if id in self.active_connections:
            for connection in self.active_connections[id]:
                await connection.send_json(message_json)


# instantiate websocket manager
ws_manager = WebSocketManager()
