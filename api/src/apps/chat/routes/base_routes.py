import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, Request, WebSocket, status
from sqlalchemy.ext.asyncio.session import AsyncSession
import redis.asyncio as redis

from src.generics.schemas import MessageResponse
from src.configurations.limiter import api_limiter
from src.apps.chat.services.websocket_services import (
    engage_chatroom_conversation,
)
from src.db.models import User
from src.apps.auth.services.jwt_services import (
    get_current_user,
    get_current_user_optional,
)
from src.apps.chat.schemas.base_schemas import (
    ChatroomCreateForm,
    ChatroomDetails,
    ChatroomDetailsExtended,
    ChatroomDetailsList,
    ChatroomPrivatePublicType,
    ChatroomUpdate,
    ChatroomUser,
    MessagesList,
)
from src.apps.chat.services.base_services import (
    create_chatroom,
    delete_chatroom,
    get_chatroom_extended_details,
    get_chatroom_messages,
    get_chatrooms_info_by_uids,
    get_currently_active_public_chatrooms,
    get_user_with_chatroom_role,
    search_chatrooms,
    update_chatroom_data,
)
from src.db.database import get_redis_session, get_session

from logging import getLogger

logger = getLogger(__name__)

base_chat_router = APIRouter()


@base_chat_router.get("", status_code=status.HTTP_200_OK)
async def get_single_chatroom(
    chatroom_identifier: UUID | str,
    db: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
    r_client: redis.Redis = Depends(get_redis_session),
) -> ChatroomDetailsExtended:
    """Get chatroom details."""
    response = await get_chatroom_extended_details(
        chatroom_identifier=chatroom_identifier, user=user, db=db, r_client=r_client
    )
    return response


@base_chat_router.post("", status_code=status.HTTP_201_CREATED)
@api_limiter.limit("2/hour")
async def create_new_chatroom(
    request: Request,
    anon_username: str,
    json: ChatroomCreateForm,
    user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session),
) -> ChatroomDetails:
    """Create new public or private chatroom."""
    response = await create_chatroom(
        json=json,
        anon_username=anon_username,
        user=user,
        db=db,
    )
    return response


@base_chat_router.patch("", status_code=status.HTTP_200_OK)
async def patch_update_chatroom(
    json: ChatroomUpdate,
    id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    r_client: redis.Redis = Depends(get_redis_session),
) -> ChatroomDetails:
    """Update chatroom data."""
    response = await update_chatroom_data(
        json=json, id=id, user=user, db=db, r_client=r_client
    )
    return response


@base_chat_router.delete("", status_code=status.HTTP_200_OK)
async def delete_user_chatroom(
    id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    r_client: redis.Redis = Depends(get_redis_session),
) -> MessageResponse:
    """Delete chatroom."""
    response = await delete_chatroom(id=id, user=user, db=db, r_client=r_client)
    return response


@base_chat_router.get("/messages/{chatroom_identifier}", status_code=status.HTTP_200_OK)
async def get_messages_from_chatroom(
    chatroom_identifier: UUID | str,
    # offset: int | None = 0,
    earliest_date: datetime.datetime | None = None,
    db: AsyncSession = Depends(get_session),
    r_client: redis.Redis = Depends(get_redis_session),
    user: User | None = Depends(get_current_user_optional),
) -> MessagesList:
    """Get paginated chatroom messages."""
    messages = await get_chatroom_messages(
        chatroom_identifier=chatroom_identifier,
        user=user,
        earliest_date=earliest_date,
        db=db,
        r_client=r_client,
        # chatroom_identifier=chatroom_identifier, user=user, offset=offset, db=db, r_client=r_client
    )
    return messages


@base_chat_router.get("/active/all")
async def get_all_active_public_chatrooms(
    db: AsyncSession = Depends(get_session),
) -> ChatroomDetailsList:
    """
    Get current active public chatrooms with users presently in chat.
    """
    response = await get_currently_active_public_chatrooms(db=db)
    return response


@base_chat_router.get("/search")
async def search_chatroom_by_name(
    search_query: str,
    db: AsyncSession = Depends(get_session),
    page: int | None = 0,
    room_type: ChatroomPrivatePublicType | None = None,
) -> ChatroomDetailsList:
    """Search for chatrooms."""
    chatroom_details = await search_chatrooms(
        search_query=search_query, page=page, room_type=room_type, db=db
    )
    return chatroom_details


@base_chat_router.get("/all")
async def get_chatrooms(
    id: str,
    db: AsyncSession = Depends(get_session),
) -> ChatroomDetailsList:
    """Get details for multiple chatrooms."""
    response = await get_chatrooms_info_by_uids(id_list_string=id, db=db)
    return response


@base_chat_router.get("/check/{id}/user")
async def get_user_membership_info(
    id: UUID,
    username: str | None = None,
    user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session),
    r_client: redis.Redis = Depends(get_redis_session),
) -> ChatroomUser:
    """Get user details with user's current role in chatroom."""
    response = await get_user_with_chatroom_role(
        id=id, user=user, username=username, db=db, r_client=r_client
    )
    return response


@base_chat_router.websocket("/engage/{chatroom_identifier}")
async def send_message_to_chat(
    websocket: WebSocket,
    chatroom_identifier: UUID | str,
    anon_username: str,
    token: str | None = None,
):
    """Enter and engage live chat."""
    r_client = websocket.app.state.r_client
    await engage_chatroom_conversation(
        websocket=websocket,
        chatroom_identifier=chatroom_identifier,
        anon_username=anon_username,
        token=token,
        r_client=r_client,
    )
