from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.configurations.limiter import api_limiter
from src.apps.chat.services.base_services import (
    clear_friend_chat,
    get_create_friend_chatroom,
    toggle_chatroom_recording_status,
)
from src.generics.schemas import MessageResponse, SortOrder
from src.apps.auth.schemas.base_schemas import PasswordForm
from src.apps.user.schemas.base_schemas import UserList, UserSortBy
from src.apps.auth.services.jwt_services import get_current_user
from src.apps.chat.schemas.base_schemas import (
    ChatroomDetails,
    ChatroomDetailsList,
    ChatroomPrivatePublicType,
    ChatroomMemberRole,
    ChatroomsSort,
)
from src.apps.chat.services.private_services import (
    add_and_unban_user_from_chat,
    add_user_to_chatroom_moderators,
    assign_chatroom_successor,
    get_user_joined_chatrooms,
    get_user_friends_with_active_chats,
    remove_user_from_chatroom_moderators,
    get_chatroom_members,
    join_chatroom,
    leave_chatroom,
    remove_and_ban_user_from_chat,
)
from src.db.database import get_session
from src.db.models import User

# from src.configurations.limiter import limiter

private_chat_router = APIRouter()


@private_chat_router.post("/join/{id}", status_code=status.HTTP_200_OK)
async def user_join_chatroom(
    id: UUID,
    json: PasswordForm | None = None,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> MessageResponse:
    """Join chatroom."""
    password = json.password if json else None
    join_chat_response = await join_chatroom(
        user=user, id=id, chatroom_password=password, db=db
    )
    return join_chat_response


@private_chat_router.post("/leave/{id}", status_code=status.HTTP_200_OK)
async def user_leave_chatroom(
    id: UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> MessageResponse:
    """Leave chatroom."""
    leave_chat_response = await leave_chatroom(user=user, id=id, db=db)
    return leave_chat_response


@private_chat_router.get(
    "/members/{id}",
    status_code=status.HTTP_200_OK,
)
async def get_members(
    id: UUID,
    role: ChatroomMemberRole | None = ChatroomMemberRole.ALL,
    sort: UserSortBy | None = UserSortBy.USERNAME,
    order: SortOrder | None = SortOrder.ASC,
    search_query: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    page: int | None = 1,
) -> UserList:
    """Get paginated chatroom members."""
    chatroom_members = await get_chatroom_members(
        id=id,
        db=db,
        user=user,
        page=page,
        sort=sort,
        order=order,
        role=role,
        search_query=search_query,
    )
    return chatroom_members


@private_chat_router.post("/members/{id}/remove", status_code=status.HTTP_200_OK)
async def remove_and_ban_user(
    id: UUID,
    user_uid: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> MessageResponse:
    """Remove/ban user from chatroom."""
    response = await remove_and_ban_user_from_chat(
        id=id, violator_uid=user_uid, user=user, db=db
    )
    return response


@private_chat_router.post("/members/{id}/add", status_code=status.HTTP_200_OK)
async def add_and_unban_user(
    id: UUID,
    user_uid: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> MessageResponse:
    """Add/unban user from chatroom."""
    response = await add_and_unban_user_from_chat(
        id=id, forgiven_uid=user_uid, user=user, db=db
    )
    return response


@private_chat_router.post("/members/{id}/add/moderator", status_code=status.HTTP_200_OK)
async def add_user_to_moderators(
    id: UUID,
    user_uid: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> MessageResponse:
    """Add user to chatroom moderators."""
    response = await add_user_to_chatroom_moderators(
        id=id, candidate_uid=user_uid, user=user, db=db
    )
    return response


@private_chat_router.post(
    "/members/{id}/remove/moderator", status_code=status.HTTP_200_OK
)
async def remove_user_from_moderators(
    id: UUID,
    user_uid: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> MessageResponse:
    """Remove user from chatroom moderators."""
    response = await remove_user_from_chatroom_moderators(
        id=id, candidate_uid=user_uid, user=user, db=db
    )
    return response


@private_chat_router.post("/members/{id}/add/successor", status_code=status.HTTP_200_OK)
async def make_user_chatroom_successor(
    id: UUID,
    user_uid: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> MessageResponse:
    """Set user as chatroom successor."""
    response = await assign_chatroom_successor(
        candidate_uid=user_uid, id=id, user=user, db=db
    )
    return response


@private_chat_router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_user_joined_chatrooms(
    role: ChatroomMemberRole | None = ChatroomMemberRole.ALL,
    room_type: ChatroomPrivatePublicType | None = ChatroomPrivatePublicType.ALL,
    sort: ChatroomsSort | None = ChatroomsSort.ACTIVITY,
    order: SortOrder | None = SortOrder.DESC,
    page: int | None = 1,
    search_query: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> ChatroomDetailsList:
    """Get paginated chatrooms that user has joined."""
    response = await get_user_joined_chatrooms(
        user=user,
        page=page,
        db=db,
        room_type=room_type,
        sort=sort,
        role=role,
        order=order,
        search_query=search_query,
    )
    return response


@private_chat_router.get("/friends/all", status_code=status.HTTP_200_OK)
async def get_friends_in_active_chat(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    page: int | None = 1,
) -> UserList:
    """Get paginated friend users that user shares open/active chat with."""
    response = await get_user_friends_with_active_chats(user=user, page=page, db=db)
    return response


@private_chat_router.get(
    "/friends/conversation",
    status_code=status.HTTP_200_OK,
)
async def get_chatroom_details_for_friend_chat(
    username: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> ChatroomDetails:
    """Get personal/friend chatroom details."""
    response = await get_create_friend_chatroom(
        user=user, candidate_username=username, db=db, create_new=False
    )
    return response


@private_chat_router.delete("/friends/conversation", status_code=status.HTTP_200_OK)
async def delete_chat_with_friends(
    username: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> MessageResponse:
    """Delete chat between user and friend."""
    response = await clear_friend_chat(user=user, friend_username=username, db=db)
    return response


@private_chat_router.patch("/recording/{id}/switch", status_code=status.HTTP_200_OK)
@api_limiter.limit("3/minute")
async def patch_chatroom_unrecorded_status(
    request: Request,
    id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> MessageResponse:
    """Toggle activate/deactivate message saving for chatroom."""
    response = await toggle_chatroom_recording_status(id=id, user=user, db=db)
    return response
