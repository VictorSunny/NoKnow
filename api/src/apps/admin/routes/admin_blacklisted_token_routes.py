from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.apps.admin.schemas.admin_base_schemas import FromDate
from src.apps.admin.schemas.admin_blacklisted_token_schemas import TokenValidity
from src.apps.auth.schemas.base_schemas import (
    BlacklistedTokenList,
    BlacklistedTokenRead,
)
from src.apps.admin.services.admin_blacklisted_token_services import (
    delete_blacklisted_user_tokens,
    get_all_blacklisted_user_tokens,
    get_user_blacklisted_token,
)
from src.apps.admin.services.admin_auth_services import (
    get_current_admin_user,
    get_current_superuser,
)
from src.db.database import get_session
from src.db.models import User
from src.generics.schemas import MessageResponse, SortByDateOrID, SortOrder

admin_blacklisted_token_router = APIRouter()


@admin_blacklisted_token_router.get("/")
async def get_blacklisted_token(
    id: int,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_admin_user),
) -> BlacklistedTokenRead:
    """
    Get blacklisted JWT token with matching id.
    """
    response = await get_user_blacklisted_token(id=id, db=db)
    return response


@admin_blacklisted_token_router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_blacklisted_tokens(
    sort: SortByDateOrID | None = SortByDateOrID.ID,
    order: SortOrder | None = SortOrder.ASC,
    validity: TokenValidity | None = TokenValidity.ALL,
    from_date: FromDate | None = FromDate.ALL,
    page: int | None = 1,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_admin_user),
) -> BlacklistedTokenList:
    """
    Get paginated blacklisted JWT tokens.
    """
    response = await get_all_blacklisted_user_tokens(
        db=db, page=page, sort=sort, order=order, validity=validity, from_date=from_date
    )
    return response


@admin_blacklisted_token_router.delete("/all", status_code=status.HTTP_200_OK)
async def remove_marked_tokens_from_blacklist(
    id: str,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_admin_user),
) -> MessageResponse:
    """
    Delete multiple JWT tokens from blacklist.
    """
    response = await delete_blacklisted_user_tokens(id=id, db=db)
    return response
