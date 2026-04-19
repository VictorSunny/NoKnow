from uuid import UUID
from fastapi import APIRouter, Depends, status

import redis.asyncio as redis

from src.apps.chat.services.base_services import get_chatroom, update_chatroom_data
from src.apps.admin.schemas.admin_base_schemas import FromDate
from src.apps.admin.services.admin_auth_services import (
    get_current_admin_user,
    get_current_superuser,
)
from src.apps.chat.schemas.base_schemas import (
    AdminChatroomCreateForm,
    ChatroomDetails,
    ChatroomDetailsList,
    ChatroomPrivatePublicType,
    ChatroomUpdate,
    ChatroomsSort,
)
from src.apps.admin.services.admin_chat_services import (
    admin_create_chatroom,
    get_all_created_chatrooms,
    mass_delete_chatrooms,
)
from src.db.database import get_redis_session, get_session
from src.db.models import User
from src.generics.schemas import MessageResponse, SortOrder
from sqlalchemy.ext.asyncio.session import AsyncSession


admin_chat_router = APIRouter()


@admin_chat_router.get("", status_code=status.HTTP_200_OK)
async def get_single_chatroom(
    id: UUID,
    db: AsyncSession = Depends(get_session),
    r_client: redis.Redis = Depends(get_redis_session),
    user: User = Depends(get_current_admin_user),
) -> ChatroomDetails:
    """
    Get chatroom for chatroom with matchig id
    """
    response = await get_chatroom(
        chatroom_identifier=id, use_case="admin view", db=db, r_client=r_client
    )
    return response


@admin_chat_router.post("", status_code=status.HTTP_201_CREATED)
async def post_create_chatroom(
    json: AdminChatroomCreateForm,
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_session),
    r_client: redis.Redis = Depends(get_redis_session),
) -> ChatroomDetails:
    """
    Create new public or private chatroom.
    """
    response = await admin_create_chatroom(json=json, db=db, r_client=r_client)
    return response


@admin_chat_router.patch("", status_code=status.HTTP_200_OK)
async def update_chatroom(
    id: UUID,
    json: ChatroomUpdate,
    db: AsyncSession = Depends(get_session),
    r_client: redis.Redis = Depends(get_redis_session),
    user: User = Depends(get_current_admin_user),
) -> ChatroomDetails:
    """
    Update chatroom data.
    """
    response = await update_chatroom_data(
        id=id, json=json, user=user, is_admin_action=True, db=db, r_client=r_client
    )
    return response


@admin_chat_router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_chatrooms(
    sort: ChatroomsSort | None = ChatroomsSort.NAME,
    order: SortOrder | None = SortOrder.ASC,
    room_type: ChatroomPrivatePublicType | None = ChatroomPrivatePublicType.ALL,
    page: int | None = 1,
    min_members: int | None = 0,
    from_date: FromDate | None = FromDate.ALL,
    search_query: str | None = None,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_admin_user),
) -> ChatroomDetailsList:
    """
    Get paginated chatrooms.
    """
    response = await get_all_created_chatrooms(
        order=order,
        sort=sort,
        page=page,
        room_type=room_type,
        min_members=min_members,
        from_date=from_date,
        search_query=search_query,
        db=db,
    )
    return response


@admin_chat_router.delete("/all", status_code=status.HTTP_200_OK)
async def delete_marked_users(
    id: str,
    user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_session),
    r_client: redis.Redis = Depends(get_redis_session),
) -> MessageResponse:
    """
    Delete multiple chatrooms.
    """
    response = await mass_delete_chatrooms(id=id, db=db, r_client=r_client)
    return response
