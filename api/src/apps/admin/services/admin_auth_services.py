from uuid import UUID
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.configurations.config import Config
from src.apps.user.schemas.base_schemas import UserRoleChoices
from src.apps.auth.services.jwt_services import decode_generic_jwt
from src.db.database import get_session
from src.db.models import User
from src.exceptions.http_exceptions import http_raise_forbidden, http_raise_unauthorized


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_admin_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_session)
) -> User:
    """
    Returns current logged in `admin` `User` using JWT value in HTTP Authorization header.
    Throws any errors raised, so a valid `admin` `User` instance must be returned.

    Args:
        token: String (expected to be JWT) extracted from request device's Authorization headers
        db: Asynchronous database connection instance

    Raises:
        HTTPException:
            401:
                -Invalid JWT
                -`User` does not exist
            403: `User` is not an `admin` user nor `superuser`
    """
    # decode access token
    # await error_if_token_is_blacklisted(token=token, token_use="access", db=db)
    payload = await decode_generic_jwt(token=token, token_use="access")

    # get user uid from decoded payload
    jwt_user_uid = UUID(payload.get("user_uid"))
    # raise error if payload contains no uid key
    if jwt_user_uid is None:
        http_raise_unauthorized("Invalid web token.")

    # get user role from decoded payload
    # confirm that jwt was created for admin user
    jwt_user_role = payload.get("role")
    if (jwt_user_role != UserRoleChoices.ADMIN) and (
        jwt_user_role != UserRoleChoices.SUPERUSER
    ):
        http_raise_forbidden(
            reason="Permission denied. Please log in through the correct channel",
            error=Config.NOT_ADMIN_ERROR,
        )

    # get user using uid extracted from payload
    user = await db.get(User, jwt_user_uid)
    if not user:
        http_raise_unauthorized("User does not exist.")
    if (user.role != UserRoleChoices.SUPERUSER) and (
        user.role != UserRoleChoices.ADMIN
    ):
        http_raise_forbidden(
            reason="User does not have permission to access this resource.",
            error=Config.NOT_ADMIN_ERROR,
        )
    return user


async def get_current_superuser(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_session)
) -> User:
    """
    Returns current logged in `superuser` using JWT value in HTTP Authorization header.
    Throws any errors raised, so a valid `superuser` instance must be returned.

    Args:
        token: String (expected to be JWT) extracted from request device's Authorization headers
        db: Asynchronous database connection instance

    Raises:
        HTTPException:
            401:
                -Invalid JWT
                -`User` does not exist
            403: `User` is not a `superuser`
    """
    # decode access token
    # await error_if_token_is_blacklisted(token=token, token_use="access", db=db)
    payload = await decode_generic_jwt(token=token, token_use="access")

    # get user uid from decoded payload
    jwt_user_uid = UUID(payload.get("user_uid"))
    # raise error if payload contains no uid key
    if jwt_user_uid is None:
        http_raise_unauthorized("Invalid web token.")

    # get user role from decoded payload
    # confirm that jwt was created for admin user
    jwt_user_role = payload.get("role")
    if (jwt_user_role != UserRoleChoices.ADMIN) and (
        jwt_user_role != UserRoleChoices.SUPERUSER
    ):
        http_raise_forbidden(
            reason="Permission denied. Please log in through the correct channel",
            error=Config.NOT_ADMIN_ERROR,
        )

    # retrieve and return user using uid extracted from payload
    user = await db.get(User, jwt_user_uid)
    if not user:
        http_raise_unauthorized("User does not exist.")
    if user.role != UserRoleChoices.SUPERUSER:
        http_raise_forbidden(
            "Permission denied. User is not a superuser.", error=Config.NOT_ADMIN_ERROR
        )
    return user
