import secrets
from urllib.parse import urlencode

import httpx
import jwt
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select

from src.configurations.config import Config
from src.apps.auth.schemas.base_schemas import AccessTokenResponse, UserCreate
from src.apps.auth.services.base_services import login_with_google, user_create
from src.db.database import get_session
from src.db.models import User
from src.exceptions.http_exceptions import (
    http_raise_bad_request,
    http_raise_unauthorized,
)

from logging import getLogger

logger = getLogger(__name__)

### IMPORT SENSITIVE ENVIRONMENT VARIABLES
GOOGLE_REDIRECT_URI = Config.GOOGLE_REDIRECT_URI
GOOGLE_CLIENT_ID = Config.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = Config.GOOGLE_CLIENT_SECRET

if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI]):
    raise RuntimeError("complete Google Oauth environment variables were not provided")

### USER PERMISSION, ACCESS TOKEN, AND USER INFO RETRIEVAL ENDPOINT
GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"

google_oauth2_router = APIRouter()


@google_oauth2_router.get("/", response_class=HTMLResponse)
async def home():
    """
    prompt page to start google oauth2
    """

    return """
    <a href="/auth/google/login">sign in with google</a>
    """


@google_oauth2_router.get("/login")
async def google_oauth2_login():
    # setup query parameters to visit google auth endpoint
    query = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    google_auth_url = f"{GOOGLE_AUTH_ENDPOINT}?{urlencode(query=query)}"
    return RedirectResponse(google_auth_url)


@google_oauth2_router.get("/callback")
async def google_oauth2_callback(
    request: Request, db: AsyncSession = Depends(get_session)
) -> AccessTokenResponse:
    """
    Login/Create user account via google oauth2
    """
    code = request.query_params.get("code")
    if not code:
        http_raise_bad_request(reason="No authorization code was provided.")
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(GOOGLE_TOKEN_ENDPOINT, data=data)
        token_data = token_response.json()
        access_token = token_data.get("access_token")

        encoded_token_id_jwt = token_data.get("id_token")
        decoded_token_id_jwt = jwt.decode(
            encoded_token_id_jwt, options={"verify_signature": False}
        )

        if not access_token:
            http_raise_bad_request(
                reason="Failed to retrieve access token from google token endpoint."
            )

        headers = {"Authorization": f"Bearer {access_token}"}
        user_info_endpoint_response = await client.get(
            GOOGLE_USERINFO_ENDPOINT, headers=headers
        )
        user_info = user_info_endpoint_response.json()

        username_id = user_info["sub"][4:8]
        user_password = secrets.token_hex(4)
        user_data = {
            "first_name": user_info["given_name"],
            "last_name": user_info["family_name"],
            "email": user_info["email"],
            "username": f'{user_info["given_name"]}{user_info["family_name"]}{username_id}',
            "google_oauth2_id": user_info["sub"],
            "password": user_password,
        }
        if decoded_token_id_jwt["email"] != user_data["email"]:
            http_raise_unauthorized(
                reason="Malicious activity detected. Retry sign in."
            )

        query = select(User).where(User.email == user_data["email"])
        query_result = await db.execute(query)

        user = query_result.scalar_one_or_none()
        if not user:
            # try to signup user
            # will raise error if user already exists in the database
            json = UserCreate(**user_data)
            user = await user_create(json=json, db=db, no_email_auth=True)

        login_response = await login_with_google(user=user, db=db)
        return login_response
