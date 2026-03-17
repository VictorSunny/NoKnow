from uuid import UUID, uuid4
from decouple import config
from jose import JWTError, jwt
from src.apps.user.schemas.base_schemas import UserRoleChoices
from src.apps.auth.schemas.base_schemas import (
    AccessTokenResponse,
    JWTUnencodedDict,
    TokenUse,
)
from src.exceptions.http_exceptions import (
    http_raise_forbidden,
    http_raise_unauthorized,
    http_raise_unprocessable_entity,
)
from src.utilities.utilities import timestamp_now

from fastapi import Depends, Request, WebSocket, WebSocketException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select

from src.utilities.utilities import timestamp_now
from src.apps.auth.schemas.base_schemas import (
    JWTUnencodedDict,
    TokenUse,
)
from src.db.database import async_session_maker, get_session
from src.db.models import BlacklistedToken, User
from src.exceptions.http_exceptions import (
    http_raise_not_found,
    http_raise_unauthorized,
)

from src.configurations.config import Config

from datetime import datetime, timedelta, timezone
from logging import getLogger

### IMPORT SENSITIVE ENVIRONMENT VARIABLES
SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("HASHING_ALGORITHM")


logger = getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def create_generic_jwt(
    json: JWTUnencodedDict, token_use: TokenUse, exp: int | None = 300
):
    """
    Creates and returns JWT.

    Args:
        json: Data to encode into JWT
        token_use: String value indentifying token creation for various use cases.
            Later used for token validation when checking if JWT is being used in correct context.
        exp: *optional* expiry time in seconds for JWT
    """
    to_encode = json.copy()
    jti = str(uuid4())

    expiry_timestamp = (datetime.now() + timedelta(seconds=exp)).astimezone(
        timezone.utc
    )
    to_encode.update({"exp": expiry_timestamp, "token_use": token_use, "jti": jti})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def decode_generic_jwt(token: str, token_use: str):
    """
    Decodes JWT and returns decoded dictionary.

    Args:
        token: JWT string
        token_use: String value indicating use case that JWT `token` is expected to have been created for

    Raises:
        HTTPException:
             401: JWT error
             422: Decoded `token` JWT did not meet up to expected `token_use`
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        http_raise_unauthorized(reason=f"JWT error.")

    if payload.get("token_use") != token_use:
        http_raise_unprocessable_entity(
            reason="Attached web token is not valid for this action."
        )
    return payload


# JWT CREATION AND VERIFICATION FUNCTIONS ---------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------


async def create_access_token(refresh_token: str, exp: int, db: AsyncSession) -> str:
    """
    Creates and returns access token.

    Args:
        refresh_token: String JWT token
        exp: time in seconds to set JWT expiry
        db: Asynchronous database connection instance

    Raises:
        HTTPException:
            401: `refresh_token` JWT is invalid
            403: `refresh_token` JWT is blacklisted
            404: `User` does not exist
    """
    await error_if_token_is_blacklisted(token=refresh_token, token_use="refresh", db=db)

    payload = await decode_generic_jwt(token=refresh_token, token_use="refresh")
    token_uid = payload.get("user_uid")
    token_sub = payload.get("sub")

    user: User = await db.get(User, UUID(token_uid))
    if not user:
        http_raise_not_found(reason="Anonymous user does not exist.")

    logger.info(f"creating access JWT for user: {user.uid} with email: {token_sub}")

    encoded_jwt = await create_generic_jwt(json=payload, token_use="access", exp=exp)
    user.last_seen = timestamp_now()
    db.add(user)
    await db.commit()

    logger.info(
        f"successfully created access JWT for user: {token_uid} with email: {token_sub}"
    )
    return encoded_jwt


async def create_refresh_token(json: JWTUnencodedDict, exp: int) -> str:
    """
    Creates and returns refresh token.

    Args:
        json: Data to be encoded into JWT
        exp: Expiry time in seconds for JWT
    """
    # logger.info(f"creating refresh token JWT for sub {json.sub}")
    logger.info(f"creating refresh JWT for user with email: {json.get("sub")}")
    encoded_refresh_token = await create_generic_jwt(
        json=json, token_use="refresh", exp=exp
    )
    logger.info(
        f"successfully created refresh JWT for user with email: {json.get("sub")}"
    )

    return encoded_refresh_token


async def blacklist_token(
    token: str, token_use: TokenUse, db: AsyncSession
) -> BlacklistedToken:
    """
    Adds JWT to blacklist.

    Args:
        token: JWT string
        token_use: String value indicating use case that JWT `token` is expected to have been created for
        db: Asynchronous database connection instance

    Raises:
        HTTPException 401: Invalid JWT
    """
    payload = await decode_generic_jwt(token=token, token_use=token_use)
    jti = payload.get("jti")
    exp = payload.get("exp")

    new_blacklisted_token = BlacklistedToken(jti=UUID(jti), exp=exp)
    db.add(new_blacklisted_token)
    await db.commit()

    return new_blacklisted_token


async def error_if_token_is_blacklisted(
    token: str, token_use: TokenUse, db: AsyncSession
):
    """
    Raises error if JWT `token` is blacklisted

    Args:
        token: JWT string
        token_use: String value indicating use case that JWT `token` is expected to have been created for
        db: Asynchronous database connection instance

    Raises:
        HTTPException 401:
            -Invalid JWT
            -JWT `token` is blacklisted
    """
    payload = await decode_generic_jwt(token=token, token_use=token_use)
    jti = payload.get("jti")

    query = select(BlacklistedToken).where(BlacklistedToken.jti == UUID(jti))
    executed_query = await db.execute(query)
    token_is_blacklisted = executed_query.scalar_one_or_none()

    if token_is_blacklisted:
        http_raise_unauthorized(reason="User is logged out.")
    return


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_session)
) -> User:
    """
    Returns current logged in `User` using JWT value in HTTP Authorization header.
    Throws any errors raised, so a valid `User` instance must be returned.

    Args:
        token: String (expected to be JWT) extracted from request device's Authorization headers
        db: Asynchronous database connection instance

    Raises:
        HTTPException:
            401:
                -Invalid JWT
                -`User` does not exist
            403: Logged in `User` account is restricted

    """
    # decode access token
    # await error_if_token_is_blacklisted(token=token, token_use="access", db=db)
    payload = await decode_generic_jwt(token=token, token_use="access")
    # get user uid from decoded payload
    user_uid = UUID(payload.get("user_uid"))
    # raise error if payload contains no uid key
    if user_uid is None:
        http_raise_unauthorized("Invalid web token.")
    # retrieve and return user using uid extracted from payload
    user = await db.get(User, user_uid)
    if not user:
        http_raise_unauthorized("User does not exist.")
    if not user.active:
        http_raise_forbidden(
            reason="User account is temporarily suspended.",
            error=Config.ACCOUNT_SUSPENDED_ERROR_CODE,
        )
    return user


async def get_current_user_optional(
    request: Request, db: AsyncSession = Depends(get_session)
) -> User | None:
    """
    Returns current logged in `User` using JWT value in HTTP Authorization header,
    or `None` if no Authorization header is passed in `Request` header.

    Args:
        token: String (expected to be JWT) extracted from request device's Authorization headers
        db: Asynchronous database connection instance

    Raises:
        HTTPException:
            401:
                -Invalid JWT
                -`User` does not exist
            403: Logged in `User` account is restricted
    """
    authorization: str = request.headers.get("Authorization")
    if not authorization:
        return None
    authorization = authorization.strip()
    if authorization[:6] != "Bearer":
        return None

    token = authorization[6:].strip()
    # decode access token
    payload = await decode_generic_jwt(token=token, token_use="access")
    # get user uid from decoded payload
    user_uid = UUID(payload.get("user_uid"))
    # raise error if payload contains no uid key
    if user_uid is None:
        http_raise_unauthorized(reason="Invalid web token.")
    # retrieve and return user using uid extracted from payload
    user = await db.get(User, user_uid)
    if not user:
        http_raise_unauthorized(reason="Anonymous user does not exist.")
    if not user.active:
        http_raise_forbidden(
            reason="User account is temporarily suspended.",
            error=Config.ACCOUNT_SUSPENDED_ERROR_CODE,
        )
    return user


async def get_current_websocker_user(token: str) -> User:
    """
    Returns current logged in `User` using JWT value in HTTP Authorization header.

    Args:
        token: String (expected to be JWT) extracted from request device's Authorization headers
    Raises:
        WwebSocketExcpetion:
            401:
                -Invalid JWT
                -`User` does not exist
            403: Logged in `User` account is restricted
    """
    token_use = "access"
    user = None
    payload = await decode_generic_jwt(token=token, token_use=token_use)
    user_uid = payload.get("user_uid")
    if user_uid is None:
        raise WebSocketException(401, "Invalid JWT.")
    user_uid = UUID(user_uid)
    async with async_session_maker() as db:
        user = await db.get(User, user_uid)
        if not user:
            raise WebSocketException(401, "User does not exist.")
        if not user.active:
            raise WebSocketException(403, "User account is temporarily suspended.")
        await db.close()

    return user


async def create_login_response(
    user: User, db: AsyncSession, user_role: UserRoleChoices
) -> JSONResponse:
    """
    Returns dict containing JWT values, along with a http-only refresh token cookie.

    Args:
        user: `User` instance
        db: Asynchronous database connection instance
        user_role: User role value added to JWT creation data before encoding

    """
    logger.info(f"creating access token and refresh token cookie for user: {user.uid}")

    access_token_expiry_seconds = 60 * Config.ACCESS_TOKEN_EXPIRY_MINUTES
    refresh_token_expiry_seconds = 60 * 60 * 24 * Config.REFRESH_TOKEN_EXPIRY_DAYS

    user_uid, user_email = str(user.uid), user.email

    # create tokens with user data
    refresh_token = await create_refresh_token(
        json={"sub": user_email, "user_uid": user_uid, "role": user_role},
        exp=refresh_token_expiry_seconds,
    )
    access_token = await create_access_token(
        refresh_token=refresh_token, exp=access_token_expiry_seconds, db=db
    )

    response_content = {"access_token": access_token, "token_type": "Bearer"}
    # set refresh token cookies and return dict containing access and refresh tokens
    response = JSONResponse(content=response_content, status_code=status.HTTP_200_OK)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=refresh_token_expiry_seconds,
        path="/",
        secure=False,
        samesite="lax",
    )

    logger.info(
        f"successfully created access JWT and refresh JWT cookie for user: {user.uid}"
    )
    return response


async def refresh_access_token(
    request: Request, db: AsyncSession
) -> AccessTokenResponse:
    """
    Returns JWT token using requesting device's http-only cookie.
    """
    # check for refresh token in device cookies
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        http_raise_unauthorized(reason="User is not logged in.")

    access_token = await create_access_token(
        refresh_token=refresh_token, exp=60 * 15, db=db
    )
    response = {"access_token": access_token, "token_type": "Bearer"}
    return response


# END OF JWT CREATION AND VERIFICATION FUNCTIONS --------------------------------------------------------
# -------------------------------------------------------------------------------------------------------
