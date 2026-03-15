from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.apps.admin.schemas.admin_base_schemas import FromDate
from src.apps.auth.schemas.base_schemas import (
    BlacklistedEmailCreate,
    BlacklistedEmailList,
    BlacklistedEmailRead,
)
from src.apps.admin.services.admin_blacklisted_email_services import (
    create_blacklisted_email,
    delete_blacklisted_user_emails,
    get_all_blacklisted_user_emails,
    get_user_blacklisted_email,
    update_blacklisted_email,
)
from src.apps.admin.services.admin_auth_services import (
    get_current_admin_user,
    get_current_superuser,
)
from src.db.database import get_session
from src.db.models import User
from src.generics.schemas import MessageResponse, SortByDateOrID, SortOrder

admin_blaclisted_email_router = APIRouter()


@admin_blaclisted_email_router.get("/")
async def get_blacklisted_email(
    id: int,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_admin_user),
) -> BlacklistedEmailRead:
    """
    Get blacklisted email with matching id.
    """
    response = await get_user_blacklisted_email(id=id, db=db)
    return response


@admin_blaclisted_email_router.post("/")
async def post_create_blacklisted_email(
    json: BlacklistedEmailCreate,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_admin_user),
) -> BlacklistedEmailRead:
    """
    Add an email address to blacklist.
    """
    response = await create_blacklisted_email(json=json, db=db)
    return response


@admin_blaclisted_email_router.patch("/")
async def post_create_blacklisted_email(
    id: int,
    json: BlacklistedEmailCreate,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_admin_user),
) -> BlacklistedEmailRead:
    """ "
    Update data for a blacklisted email address.
    """
    response = await update_blacklisted_email(id=id, json=json, db=db)
    return response


@admin_blaclisted_email_router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_blacklisted_emails(
    sort: SortByDateOrID | None = SortByDateOrID.ID,
    order: SortOrder | None = SortOrder.ASC,
    from_date: FromDate | None = FromDate.ALL,
    page: int | None = 1,
    search_query: str | None = None,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_admin_user),
) -> BlacklistedEmailList:
    """
    Get paginated blacklisted emails.
    """
    response = await get_all_blacklisted_user_emails(
        db=db,
        page=page,
        sort=sort,
        order=order,
        from_date=from_date,
        search_query=search_query,
    )
    return response


@admin_blaclisted_email_router.delete("/all", status_code=status.HTTP_200_OK)
async def remove_marked_emails_from_blacklist(
    id: str,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_superuser),
) -> MessageResponse:
    """
    Remove email address from blacklist.
    """
    response = await delete_blacklisted_user_emails(id=id, db=db)
    return response
