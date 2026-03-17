from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.generics.schemas import MessageResponse
from src.apps.auth.routes.base_routes import base_auth_router
from src.apps.auth.routes.google_oauth2_routes import google_oauth2_router
from src.apps.user.routes.base_routes import base_user_router
from src.apps.chat.routes.base_routes import base_chat_router
from src.apps.chat.routes.private_routes import private_chat_router

from src.apps.admin.routes.admin_auth_routes import admin_auth_router
from src.apps.admin.routes.admin_blacklisted_email_routes import (
    admin_blaclisted_email_router,
)
from src.apps.admin.routes.admin_chat_routes import admin_chat_router
from src.apps.admin.routes.admin_user_routes import admin_user_router
from src.apps.admin.routes.admin_blacklisted_token_routes import (
    admin_blacklisted_token_router,
)

from src.configurations.exception_handler import register_app_exceptions

from src.configurations.logger import set_up_logging
from src.configurations.limiter import api_limiter

from logging import getLogger

FRONTEND_HOSTNAME = os.environ.get("FRONTEND_HOSTNAME") or "frontend"
FRONTEND_PORT = os.environ.get("FRONTEND_PORT") or "5173"

logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    set_up_logging()
    logger.info("server started")
    yield
    logger.info("server interrupted")


app = FastAPI(
    title="NoKnow",
    description="Social site for anonymous chats",
    version="v1",
    lifespan=lifespan,
    docs_url="/docs",
)

register_app_exceptions(app=app)
app.state.limiter = api_limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
async def home() -> MessageResponse:
    return {"message": "Welcome home."}


app.include_router(base_auth_router, prefix="/auth", tags=["auth"])
app.include_router(
    google_oauth2_router, prefix="/auth/google", tags=["auth, google, oauth2"]
)
app.include_router(base_user_router, prefix="/user", tags=["user"])
app.include_router(base_chat_router, prefix="/chat", tags=["chat"])
app.include_router(
    private_chat_router, prefix="/chat/private/room", tags=["chat, protected"]
)

app.include_router(admin_auth_router, prefix="/admin/auth", tags=["admin, auth"])
app.include_router(admin_user_router, prefix="/admin/user", tags=["admin, user"])
app.include_router(admin_chat_router, prefix="/admin/chat", tags=["admin, chat"])
app.include_router(
    admin_blaclisted_email_router,
    prefix="/admin/email_blacklist",
    tags=["admin, email, blacklist"],
)
app.include_router(
    admin_blacklisted_token_router,
    prefix="/admin/token_blacklist",
    tags=["admin, token, blacklist"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # local frontend
        "http://localhost:4173",
        "http://localhost:5173",
        "http://localhost:3000",
        # docker frontend
        # dev
        f"http://frontend:4173",
        f"http://frontend:5173",
        # production
        f"http://{FRONTEND_HOSTNAME}:{FRONTEND_PORT}",
    ],
    allow_methods=["*"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    allow_credentials=True,
)
