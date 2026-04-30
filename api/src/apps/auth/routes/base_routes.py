from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio.session import AsyncSession

import redis.asyncio as redis

from src.apps.auth.services.base_services import (
    delete_user_with_confirmation_text,
    get_is_two_factor_authenticated_status,
    login,
    logout,
    update_user_hidden_status,
    user_create,
    user_update_basic_info,
    user_update_email,
    user_update_is_two_factor_authenticated,
    user_update_password,
)
from src.apps.user.schemas.base_schemas import UserPrivate
from src.apps.auth.services.verification_services import check_user_data_is_acceptable
from src.generics.schemas import ConfirmationText, IsValidResponse, MessageResponse
from src.configurations.limiter import api_limiter
from src.generics.validation_services import password_check_response
from src.apps.auth.services.otp_services import (
    confirm_otp_code_create_otp_jwt,
    create_send_cache_otp,
)
from src.apps.auth.schemas.base_schemas import (
    AccessTokenResponse,
    EmailForm,
    EmailUsernameForm,
    LoginForm,
    OTPForm,
    OTPJWTResponse,
    PasswordForm,
    UserBasicUpdate,
    UserCreate,
    UserEmailPasswordForm,
    UserHiddenStatus,
    UserPasswordUpdate,
    UserTwoFactorAuthStatus,
)
from src.apps.auth.schemas.base_schemas import OTPType
from src.apps.auth.services.jwt_services import (
    get_current_user,
    get_current_user_optional,
    refresh_access_token,
)

from src.db.database import get_redis_session, get_session
from src.db.models import User

base_auth_router = APIRouter()


@base_auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    json: UserCreate, otp_token: str, db: AsyncSession = Depends(get_session)
) -> UserPrivate:
    """
    Signup/create new user account.
    """
    signup_response = await user_create(json=json, db=db, otp_token=otp_token)
    return signup_response


@base_auth_router.patch("", status_code=status.HTTP_200_OK)
async def update_user_details(
    json: UserBasicUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    r_client: redis.Redis = Depends(get_redis_session),
) -> UserPrivate:
    """
    Update user data.
    """
    response = await user_update_basic_info(
        user=user, json=json, db=db, r_client=r_client
    )
    return response


@base_auth_router.post("/data/check", status_code=status.HTTP_200_OK)
async def check_user_exists(
    json: EmailUsernameForm, db: AsyncSession = Depends(get_session)
) -> MessageResponse:
    """
    Check if signup credentials have any issues.
    """
    check_response = await check_user_data_is_acceptable(
        email=json.email, username=json.username, db=db
    )
    return check_response


@base_auth_router.post("/login", status_code=status.HTTP_200_OK)
async def user_login(
    json: LoginForm,
    otp_token: str | None = None,
    db: AsyncSession = Depends(get_session),
    r_client: redis.Redis = Depends(get_redis_session),
) -> AccessTokenResponse:
    """
    Login to user account.
    """
    login_response = await login(
        otp_token=otp_token, json=json, db=db, r_client=r_client
    )
    return login_response


@base_auth_router.post("/logout", status_code=status.HTTP_200_OK)
async def user_logout(
    request: Request,
    db: AsyncSession = Depends(get_session),
) -> MessageResponse:
    """
    Logout of user account.
    """
    response = await logout(request=request, db=db)
    return response


@base_auth_router.get("/token", status_code=status.HTTP_200_OK)
async def get_jwt(
    request: Request,
    db: AsyncSession = Depends(get_session),
) -> AccessTokenResponse:
    """
    Get fresh access token.
    """
    response = await refresh_access_token(request=request, db=db)
    return response


@base_auth_router.patch("/email", status_code=status.HTTP_200_OK)
async def change_user_email(
    json: UserEmailPasswordForm,
    otp_token: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    r_client: redis.Redis = Depends(get_redis_session),
) -> MessageResponse:
    """
    Update email for user account.
    """
    response = await user_update_email(
        json=json, otp_token=otp_token, user=user, db=db, r_client=r_client
    )
    return response


@base_auth_router.patch("/password", status_code=status.HTTP_200_OK)
async def change_user_password(
    json: UserPasswordUpdate | None = None,
    otp_token: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    r_client: redis.Redis = Depends(get_redis_session),
) -> MessageResponse:
    """
    Update password for user account.
    """
    response = await user_update_password(
        json=json, otp_token=otp_token, db=db, user=user, r_client=r_client
    )
    return response


@base_auth_router.post("/otp/request", status_code=status.HTTP_202_ACCEPTED)
async def otp_code_request(
    json: EmailForm,
    use_case: OTPType,
    r_client: redis.Redis = Depends(get_redis_session),
) -> MessageResponse:
    """
    Request for OTP code.
    """
    email = json.email
    response = await create_send_cache_otp(
        sub=email, otp_type=use_case, r_client=r_client
    )
    return response


@base_auth_router.post("/otp/token", status_code=status.HTTP_200_OK)
async def get_otp_token(
    json: OTPForm,
    use_case: OTPType,
    r_client: redis.Redis = Depends(get_redis_session),
) -> OTPJWTResponse:
    """
    Get validation JWT by providing valid OTP code.
    """
    otp, email = json.otp, json.email
    response = await confirm_otp_code_create_otp_jwt(
        sub=email, code=otp, otp_type=use_case, r_client=r_client
    )
    return response


@base_auth_router.patch("/two_factor_authentication", status_code=status.HTTP_200_OK)
async def is_two_factor_authenticated_switch(
    json: PasswordForm,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    r_client: redis.Redis = Depends(get_redis_session),
) -> UserTwoFactorAuthStatus:
    """
    Toggle activate/deactivate two factor authentication for user.
    """
    response = await user_update_is_two_factor_authenticated(
        user=user, password=json.password, db=db, r_client=r_client
    )
    return response


@base_auth_router.post("/two_factor_authentication", status_code=status.HTTP_200_OK)
async def get_user_two_factor_auth_status(
    json: EmailForm | None = None,
    user: User = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session),
    r_client: redis.Redis = Depends(get_redis_session),
) -> UserTwoFactorAuthStatus:
    """
    Get user two factor authentication security status.
    """
    response = await get_is_two_factor_authenticated_status(
        json=json, user=user, db=db, r_client=r_client
    )
    return response


@base_auth_router.get("/privacy", status_code=status.HTTP_200_OK)
async def is_hidden_status(
    user: User = Depends(get_current_user),
) -> UserHiddenStatus:
    """
    Get user hidden status
    """
    return user


@api_limiter.limit("3/minute")
@base_auth_router.patch("/privacy", status_code=status.HTTP_200_OK)
async def is_hidden_switch(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    r_client: redis.Redis = Depends(get_redis_session),
) -> UserHiddenStatus:
    """
    Update user hidden status.
    """
    response = await update_user_hidden_status(user=user, db=db, r_client=r_client)
    return response


@base_auth_router.post("/confirm/password", status_code=status.HTTP_200_OK)
async def confirm_user_password(
    json: PasswordForm, user: User = Depends(get_current_user)
) -> IsValidResponse:
    """
    Confirm password for user account.
    """
    response = await password_check_response(password=json.password, user=user)
    return response


@base_auth_router.post("/confirm_delete", status_code=status.HTTP_200_OK)
async def delete_user_account(
    json: ConfirmationText,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    r_client: redis.Redis = Depends(get_redis_session),
) -> MessageResponse:
    """
    Delete user account.
    """
    response = await delete_user_with_confirmation_text(
        user=user, json=json, db=db, r_client=r_client
    )
    return response
