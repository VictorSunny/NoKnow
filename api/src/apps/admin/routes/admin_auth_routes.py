from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.apps.auth.schemas.base_schemas import AccessTokenResponse, LoginForm
from src.apps.auth.services.base_services import login
from src.db.database import get_session


admin_auth_router = APIRouter()


@admin_auth_router.post("/login")
async def login_admin_user(
    json: LoginForm, db: AsyncSession = Depends(get_session)
) -> AccessTokenResponse:
    """
    Login to admin user account.
    """
    response = await login(json=json, db=db, is_admin_action=True)
    return response
