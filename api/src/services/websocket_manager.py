import ast
import asyncio
from typing import Dict, List
from uuid import UUID
from fastapi import FastAPI, WebSocket, WebSocketException
from redis import RedisError
from sqlalchemy import exists
from sqlmodel import select

import redis.asyncio as redis

from src.configurations.config import Config
from src.db.database import async_session_maker
from src.apps.chat.schemas.base_schemas import ChatroomType, MessageRead
from src.db.models import Chatroom, User, UserChatroomLink

from logging import getLogger

logger = getLogger(__name__)


class WebSocketManager:
    """
    `WebSocketManager` class handles `Chatroom` `WebSocket` connections.
    """

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def start(self, app: FastAPI):
        self.r_client = app.state.r_client

    async def get_active_chatrooms(self):
        """
        Returns 40(max) most recent chatrooms that are currently engaged with at least one user.
        """
        active_chatrooms = await self.r_client.smembers(
            Config.REDIS_ACTIVE_CHATROOMS_NAME_PREFIX
        )
        active_chatrooms = list(active_chatrooms)[:50]
        return active_chatrooms

    async def add_to_active_chatrooms(self, id: UUID):
        await self.r_client.sadd(Config.REDIS_ACTIVE_CHATROOMS_NAME_PREFIX, str(id))

    async def remove_from_active_chatrooms(self, id: UUID):
        await self.r_client.srem(Config.REDIS_ACTIVE_CHATROOMS_NAME_PREFIX, str(id))

    async def get_chatroom_active_users(self, id: UUID) -> int:
        """
        Returns total number of `WebSocket`s actively connected to `Chatroom` websocket connection

        Args:
            if: UUID for `Chatroom` to check
        """
        active_websockets_connection_to_chatroom = await self.r_client.get(
            f"{Config.REDIS_CHATROOM_ACTIVE_USERS_COUNT_PREFIX}:{str(id)}"
        )
        print("acitve users:", active_websockets_connection_to_chatroom)
        if not active_websockets_connection_to_chatroom:
            return 0
        return int(active_websockets_connection_to_chatroom)

    async def connect(self, chatroom: Chatroom, user: User, websocket: WebSocket):
        """
        Adds `WebSocket` to `Chatroom` websocket connections.

        Args:
            id: UUID for `Chatroom` to add `WebSocket`
            user: *optional* `User` instance
            websocker: `WebSocket` instance
        """
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
            async with async_session_maker() as db:
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

                await db.close()

        await websocket.accept()
        self.active_connections.setdefault(str(chatroom.uid), []).append(websocket)
        print("increasing count")
        await self.r_client.incr(
            f"{Config.REDIS_CHATROOM_ACTIVE_USERS_COUNT_PREFIX}:{str(id)}"
        )

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
        id = str(id)
        if (id in self.active_connections) and (
            websocket in self.active_connections[id]
        ):
            self.active_connections[id].remove(websocket)
            print("decreading count")
            await self.r_client.decr(
                f"{Config.REDIS_CHATROOM_ACTIVE_USERS_COUNT_PREFIX}:{str(id)}"
            )
            # delete chatroom websocket connection if empty
            if len(self.active_connections) < 1:
                del self.active_connections[id]
                logger.info(f"websocket connection for chat: {id} closed")

    async def alert_current_websocket(
        self, message_json: MessageRead, websocket: WebSocket, response_code: int
    ):
        """
        Sends a warning message to a single `WebSocket`
        """
        message_json.update({"response_code": response_code})
        await websocket.send_json(message_json)

    # send message to all users in active websocket connection for chatroom

    async def broadcast(self, id: UUID, message_json: MessageRead):
        id = str(id)
        if id in self.active_connections:
            for connection in self.active_connections[id]:
                await connection.send_json(message_json)

    async def publish(self, id: UUID, message_content: MessageRead):
        await self.r_client.publish(
            f"{Config.REDIS_CHATROOM_WEBSOCKET_CONNECTION_NAME_PREFIX}:{str(id)}",
            str(message_content),
        )


# instantiate websocket manager
ws_manager = WebSocketManager()
