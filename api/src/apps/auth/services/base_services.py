from json import JSONDecodeError
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

import redis.asyncio as redis

from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.caching.services.redis_user_caching import clear_user_cache, set_user_cache
from src.configurations.config import Config
from src.apps.user.schemas.base_schemas import UserRoleChoices
from src.apps.user.services.base_services import get_user_by_email
from src.generics.schemas import ConfirmationText, MessageResponse
from src.generics.validation_services import error_if_model_password_incorrect
from src.apps.auth.services.otp_services import confirm_otp_jwt
from src.apps.auth.schemas.base_schemas import (
    EmailForm,
    LoginForm,
    UserAdminUserRoleChoices,
    UserBasicUpdate,
    UserCreate,
    UserCreateComplete,
    UserEmailPasswordForm,
    UserPasswordUpdate,
    UserTwoFactorAuthStatus,
)
from src.apps.auth.services.jwt_services import (
    blacklist_token,
    create_login_response,
)
from src.apps.auth.services.verification_services import (
    check_user_data_is_acceptable,
    error_if_email_in_db,
    error_if_username_in_db,
)
from src.db.models import (
    User,
)
from src.exceptions.http_exceptions import (
    http_raise_forbidden,
    http_raise_unauthorized,
    http_raise_unprocessable_entity,
)
from src.utilities.utilities import (
    check_password,
    hash_password,
)

from logging import getLogger

logger = getLogger(__name__)


async def verify_user(
    email: str, password: str, db: AsyncSession, r_client: redis.Redis
) -> User:
    """
    Confirms if `User` password.

    Args:
        email: String for `User`
        password: String to check against
        db: Asynchronous database connection instance

    Raises:
        HTTPException:
            401: `password` is invalid for `User`
            403: `User` password has not been set
            404: `User` does not exist
    """
    user = await get_user_by_email(email=email, db=db, r_client=r_client)

    if not user.password:
        http_raise_forbidden(
            reason="User password not set. Set password with email through account recovery process."
        )
    password_verified = check_password(password, user.password)
    if not password_verified:
        http_raise_unauthorized(reason="Invalid password.")

    return user


async def login(
    db: AsyncSession,
    r_client: redis.Redis,
    json: OAuth2PasswordRequestForm | LoginForm,
    otp_token: str | None = None,
    is_admin_action: bool | None = False,
) -> JSONResponse:
    """
    Returns JWT token, and http-only token for refresh if provided with valid credentials.

    Args:
        db: Asynchronous database connection instance
        json: Form with redentials for `login`
        otp_token: *optional* JWT string value needed if `User` is two factor authenticated
        is_admin_action: *optional* idicates that this function is being called in an admin user context

    Raises:
        HTTPException:
            401:
                -`otp_token` JWT invalid
                -Suspicious activity detected while processing `otp_token` JWT
                -`User` two factor authentication is `on` and no valid `otp_token` JWT value was provided
            403:
                -`User` account is suspended
                -`User` is not an admin user and `is_admin_action` is set to True,
                    meaning  this function is being used in an admin context


    """
    email, password = json.email, json.password

    logger.info(f"starting login for user with email: {email}, {password}")

    user = await verify_user(email=email, password=password, db=db, r_client=r_client)

    if not user.active:
        http_raise_forbidden(
            reason="Your account is temporarily suspended.",
            error=Config.ACCOUNT_SUSPENDED_ERROR_CODE,
        )

    if user.is_two_factor_authenticated:
        if not otp_token:
            http_raise_unauthorized(
                reason="User two factor authentication is active and login OTP token was not provided."
            )
        await confirm_otp_jwt(
            token=otp_token, expected_sub=email, expected_otp_type="login"
        )

    if (
        is_admin_action
        and (user.role != UserRoleChoices.ADMIN)
        and (user.role != UserRoleChoices.SUPERUSER)
    ):
        http_raise_forbidden(
            reason="User is not allowed to login through this channel. Please login through an authorized channel."
        )

    role = user.role if is_admin_action else UserRoleChoices.USER
    response = await create_login_response(user=user, db=db, user_role=role)

    logger.info(f"successfully logged in user: {user.uid} with email: {user.email}")

    return response


async def login_with_google(user: User, db: AsyncSession) -> JSONResponse:
    """
    Returns JWT token, and http-only token for refresh for `User`.

    Args:
        user: `User` instance for token creation
        db: Asynchronous database connection instance
    """

    logger.info(f"logging in google oauth2 user: {user.uid} with email {user.email}")

    response = await create_login_response(
        user=user, db=db, user_role=UserRoleChoices.USER
    )

    logger.info(
        f"successfully logged in google oauth2 user with email: {user.email} | uid: {user.uid}"
    )
    return response


async def logout(request: Request, db: AsyncSession) -> JSONResponse:
    """
    Blacklists and clears http_only request token from requesting device.
    """

    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        http_raise_unauthorized(reason="User is not logged in.")

    await blacklist_token(token=refresh_token, token_use="refresh", db=db)
    # set refresh token cookies and return dict containing access and refresh tokens
    response = JSONResponse(
        content={"message": "Successfully logged out user."},
        status_code=status.HTTP_200_OK,
    )
    response.delete_cookie(
        key="refresh_token", httponly=True, samesite="lax", path="/", secure=False
    )

    return response


async def user_create(
    json: UserCreate | UserCreateComplete,
    db: AsyncSession,
    role: UserAdminUserRoleChoices | None = UserAdminUserRoleChoices.USER,
    no_email_auth: bool | None = False,
    otp_token: str | None = None,
) -> User:
    """
    Create new user using signup `json` form.

    Args:
        json: Signup data
        db: Asynchronous database connection instance
        role: *optional* `User` role. defaults to "user" if none is provided to create a normal, non-admin user
        otp_token: *optional* JWT for signup. Must be provided if `no_email_auth` is False
        no_email_auth: *optional* determines whether error will be raised when no `otp_token` value is provided

    Raises:
        HTTPException:
            401:
                -No `otp_token` value was provided and `no_email_auth` is False
                -JWT invalid
            409: Signup data contains field values that break `User` table unique constraints
    """

    email, username, password = (
        json.email,
        json.username,
        json.password,
    )

    # check user email has not been blacklisted - suspended
    # raise error if user has been suspended
    if (not no_email_auth) and (not otp_token):
        http_raise_unauthorized(reason="No token provided.")
    if not no_email_auth:
        await confirm_otp_jwt(
            token=otp_token, expected_sub=email, expected_otp_type="signup"
        )

    logger.info(f"creating new user with email: {email} and username {username}")

    await check_user_data_is_acceptable(email=email, username=username, db=db)

    hashed_password = hash_password(password=password)

    user_data = UserCreate(**json.model_dump())
    new_user = User.model_validate(user_data)
    new_user.role = role
    new_user.password = hashed_password

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    logger.info(
        f"successfully created new user with email: {new_user.email} and uid {new_user.uid}"
    )

    return new_user


# END OF USER CREATION, UPDATE AND VERIFICATION FUNCTIONS ---------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------


# USER UPDATE FUNCTIONS ---------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------


async def user_update_basic_info(
    user: User, json: UserBasicUpdate, db: AsyncSession, r_client: redis.Redis
) -> User:
    """
    Updates logged in `User`'s data.

    Args:
        user: Logged in `User`
        json: Update data
        db: Asynchronous database connection instance

    Raises:
        HTTPException:
            409: Update data contains field value that breaks `User` table unique constraints
            422:
                -`json` is empty
                -No changes detected between logged in `User` instance field values and `json` update data
    """

    # check if update form username exists in database if new username does not match current username
    logger.info(f"updating basic data for user: {user.uid}")

    # check if form is fully filled and if there are changes between current user data and form data
    if json.username and json.username.lower() == user.username.lower():
        if json.bio and json.bio == user.bio:
            if json.first_name and json.first_name.lower() == user.first_name.lower():
                if json.last_name and json.last_name.lower() == user.last_name.lower():
                    if json.is_hidden == user.is_hidden:
                        http_raise_unprocessable_entity(reason="No changes detected.")

    if json.username:
        if user.username.lower() != json.username.lower():
            await error_if_username_in_db(username=json.username, db=db)

    json = json.model_dump(exclude_unset=True)
    # raise error if form is empty
    if not JSONDecodeError:
        http_raise_unprocessable_entity(reason="Please fill at least one field.")
    # update model

    await clear_user_cache(user=user, r_client=r_client)
    query = update(User).where(User.uid == user.uid).values(**json)
    await db.execute(query)
    await db.commit()

    user = await db.get(User, user.uid)
    await set_user_cache(user=user, r_client=r_client)

    logger.info(f"successfully updated basic data for user: {user.uid}")
    return user


async def user_update_email(
    user: User,
    json: UserEmailPasswordForm,
    otp_token: str,
    db: AsyncSession,
    r_client: redis.Redis,
) -> MessageResponse:
    """
    Updates `User` email.

    Args:
        user: Logged in `User` instance
        json: Update data containing neccessary credentials
        otp_token: JWT for authorizing update
        db: Asynchronous database connection instance

    Raises:
        HTTPException:
            401: JWT error
            403: Invalid verification credentails
            409: Update `email` already is use by some `User` row in database

    """
    # set error for email exists
    old_email = user.email
    # extract values from json form
    new_email, password = json.email, json.password

    logger.info(f"updating email for user: {user.uid}")

    # verfiy password entered by user to validate update
    await verify_user(email=old_email, password=password, db=db, r_client=r_client)
    # verify that new email isn't being used by any user in the database
    await error_if_email_in_db(email=new_email, db=db)
    # verify otp_token is valid
    await confirm_otp_jwt(
        token=otp_token, expected_sub=new_email, expected_otp_type="email_change"
    )

    await clear_user_cache(user=user, r_client=r_client)
    # update user email with new email
    query = update(User).where(User.uid == user.uid).values(email=new_email)
    await db.execute(query)
    await db.commit()

    logger.info(
        f"successfully updated email for user: {user.uid} from {old_email} to {new_email}"
    )
    return {"message": f"successfully updated email from {old_email} to {new_email}"}


async def user_update_password(
    user: User,
    json: UserPasswordUpdate | None,
    otp_token: str | None,
    db: AsyncSession,
    r_client: redis.Redis,
) -> MessageResponse:
    """
    Update user password

    Args:
        user: Logged in `User` instance
        otp_token: JWT for authorizing update
        json: Update data containing neccessary credentials
        db: Asynchronous database connection instance

    Raises:
        HTTPException:
            401:
                -JWT error
                -No `otp_token` value was provided, and update `json` has no `old_password` attribute
            403: Invalid verification credentails
            422:
                -Invalid JWT token
                -New password is same as previous
    """
    logger.info(f"updating password for user: {user.uid}")

    old_password, password = (
        json.old_password,
        json.password,
    )
    if otp_token:
        await confirm_otp_jwt(
            token=otp_token,
            expected_sub=user.email,
            expected_otp_type="password_change",
        )
    else:
        if not old_password:
            http_raise_unprocessable_entity(
                reason="Previous password was not provided."
            )
        if user.password:
            await error_if_model_password_incorrect(
                model_name="user", password=old_password, hashed_password=user.password
            )

    if user.password:
        password_same_as_previous = check_password(
            password=password, hashed_password=user.password
        )
        if password_same_as_previous:
            http_raise_unprocessable_entity(
                reason="new password cannot be the same as previous"
            )

    hashed_password = hash_password(password=password)
    user.password = hashed_password

    await clear_user_cache(user=user, r_client=r_client)
    query = update(User).where(User.uid == user.uid).values(password=hashed_password)
    await db.execute(query)
    await db.commit()

    logger.info(f"successfully update password for user: {user.uid}")

    return {"message": "password successfully changed"}


async def user_update_is_two_factor_authenticated(
    user: User, password: str, db: AsyncSession, r_client: redis.Redis
) -> UserTwoFactorAuthStatus:
    """
    Toggle activate/deactivates two factor authentication security for logged in `User`.

    Args:
        user: Logged in `User` instance
        password: String value for verification
        db: Asynchronous database connection instance

    Raises:
        HTTPException:
            403:
                -Logged in `User` has not set password
                -`password` invalid for logged in `User` instance
    """
    logger.info(f"updating two-factor authentication security for user: {user.uid}")

    if not user.password:
        http_raise_forbidden(
            reason="User password not set. Set password with email through account recovery process."
        )
    await error_if_model_password_incorrect(
        model_name="user", password=password, hashed_password=user.password
    )

    await clear_user_cache(user=user, r_client=r_client)
    query = (
        update(User)
        .where(User.uid == user.uid)
        .values(is_two_factor_authenticated=(not user.is_two_factor_authenticated))
    )
    await db.execute(query)
    await db.commit()

    tfa_status = "activated" if user.is_two_factor_authenticated else "deactivated"
    logger.info(
        f"updated two-factor authentication security for user: {user.uid}. currently {tfa_status}"
    )

    user = await db.get(User, user.uid)
    await set_user_cache(user=user, r_client=r_client)
    return user


async def get_is_two_factor_authenticated_status(
    user: User | None, json: EmailForm | None, db: AsyncSession, r_client: redis.Redis
) -> User:
    """
    Check user two factor authentication security status.

    Args:
        user: Logged in `User` instance
        json: Form containing `email`
        db: Asynchronous database connection instance

    Raises:
        HTTPException:
            404: `User` does not exist
            409: Update `email` already is use by some `User` row in database
    """
    if not user and not json:
        http_raise_unauthorized("User is not logged in and no email data was provided.")
    if json:
        user = await get_user_by_email(email=json.email, db=db, r_client=r_client)

    logger.info(
        f"returning user: {user.uid} for two-factor authentication status check."
    )
    return user


async def update_user_hidden_status(
    user: User, db: AsyncSession, r_client: redis.Redis
) -> User:
    """
    Toggle activates/deactivates `User`'s hidden status.

    Args:
        user: Logged in `User` instance
        db: Asynchronous database connection instance
    """
    await clear_user_cache(user=user, r_client=r_client)
    query = (
        update(User).where(User.uid == user.uid).values(is_hidden=(not user.is_hidden))
    )
    await db.execute(query)
    await db.commit()

    user = await db.get(User, user.uid)
    await set_user_cache(user=user, r_client=r_client)
    return user


# DELETE USER ACCOUNT
async def delete_user_with_confirmation_text(
    user: User, json: ConfirmationText, db: AsyncSession, r_client: redis.Redis
) -> MessageResponse:
    """
    Deletes logged in `User` instance.

    Args:
        user: Logged in `User`
        json: Form containing verification data for action
        db: Asynchronous database connection instance

    Raises:
        HTTPException 422: `json` data is invalid
    """
    expected_json_text = f"I {user.username} want to delete my account"
    recieved_text = json.text

    if expected_json_text.lower() != recieved_text.lower():
        http_raise_unprocessable_entity(
            reason=f"Incorrect json text. Type: {expected_json_text}"
        )

    await clear_user_cache(user=user, r_client=r_client)
    query = delete(User).where(User.uid == user.uid)
    await db.execute(query)
    await db.commit()
    return {"message": "Account deleted. Sorry to see you go."}
