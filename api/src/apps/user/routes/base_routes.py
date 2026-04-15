from uuid import UUID
from fastapi import APIRouter, Depends, status

import redis.asyncio as redis

from src.apps.auth.services.jwt_services import get_current_user
from src.apps.user.schemas.base_schemas import (
    FriendshipStatus,
    UserList,
    UserSortBy,
)
from src.apps.user.services.base_services import (
    accept_friend_request,
    cancel_friend_request,
    check_frienship_status_by_username,
    get_user_details,
    get_user_friend_requests,
    get_user_friends,
    get_user_sent_friend_requests,
    reject_friend_request,
    remove_friend,
    search_users,
    send_friend_request,
)
from src.db.database import get_redis_session, get_session
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User
from src.generics.schemas import MessageResponse, SortOrder

base_user_router = APIRouter()


@base_user_router.get("", status_code=status.HTTP_200_OK)
async def get_user(
    username: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Get user details."""
    response = await get_user_details(user=user, username=username, db=db)
    # return user_info_response
    return response


@base_user_router.get("/search", status_code=status.HTTP_200_OK)
async def search_for_users(
    search_query: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> UserList:
    """Search users. Returns paginated users."""
    res = await search_users(query=search_query, user=user, db=db)
    return res


@base_user_router.get("/friends/all", status_code=status.HTTP_200_OK)
async def get_all_friends(
    sort: UserSortBy | None = UserSortBy.USERNAME,
    order: SortOrder | None = SortOrder.ASC,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    page: int | None = 1,
    search_query: str | None = None,
) -> UserList:
    """Get paginated friend users."""
    response = await get_user_friends(
        user=user, db=db, page=page, sort=sort, order=order, search_query=search_query
    )
    return response


@base_user_router.get(
    "/friends/requests/all",
    status_code=status.HTTP_200_OK,
)
async def get_all_friend_requests(
    sort: UserSortBy | None = UserSortBy.DATE,
    order: SortOrder | None = SortOrder.DESC,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    page: int | None = 1,
) -> UserList:
    """Get paginated users with pending friend request sent."""
    response = await get_user_friend_requests(
        user=user, db=db, sort=sort, order=order, page=page
    )
    return response


@base_user_router.get(
    "/friends/requests/sent/all",
    status_code=status.HTTP_200_OK,
)
async def get_all_sent_friend_requests(
    sort: UserSortBy | None = UserSortBy.DATE,
    order: SortOrder | None = SortOrder.DESC,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    page: int | None = 1,
) -> UserList:
    """Get paginated users that have not responded to logged in user's friend request."""
    response = await get_user_sent_friend_requests(
        user=user, db=db, page=page, sort=sort, order=order
    )
    return response


@base_user_router.post("/friends/requests/send", status_code=status.HTTP_200_OK)
async def send_user_friend_request(
    id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> MessageResponse:
    """Send friend request to user."""
    response = await send_friend_request(user=user, candidate_uid=id, db=db)
    return response


@base_user_router.post("/friends/requests/unsend", status_code=status.HTTP_200_OK)
async def unsend_friend_request(
    id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> MessageResponse:
    """Cancel friend request sent to user."""
    response = await cancel_friend_request(user=user, candidate_uid=id, db=db)
    return response


@base_user_router.post("/friends/requests/accept", status_code=status.HTTP_200_OK)
async def accept_user_friend_request(
    id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> MessageResponse:
    """Accept friend request from user."""
    response = await accept_friend_request(user=user, candidate_uid=id, db=db)
    return response


@base_user_router.post("/friends/requests/reject", status_code=status.HTTP_200_OK)
async def reject(
    id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> MessageResponse:
    """Reject friend request from user."""
    response = await reject_friend_request(user=user, candidate_uid=id, db=db)
    return response


@base_user_router.post("/friends/remove", status_code=status.HTTP_200_OK)
async def unfriend_user(
    id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    r_client: redis.Redis = Depends(get_redis_session),
) -> MessageResponse:
    """Remove user from friends."""
    response = await remove_friend(
        user=user, candidate_uid=id, db=db, r_client=r_client
    )
    return response


@base_user_router.get("/friends/check", status_code=status.HTTP_200_OK)
async def check_friendship(
    username: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> FriendshipStatus:
    """Check if user is a friend."""
    response = await check_frienship_status_by_username(
        candidate_username=username, user=user, db=db
    )
    return response
