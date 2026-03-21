import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.configurations.config import Config
from src.db.database import get_session
from src.main import app

import redis.asyncio as redis

TEST_DATABASE_URL = "sqlite+aiosqlite:///test_db.sqlite3"


engine = create_async_engine(TEST_DATABASE_URL, echo=False)
async_test_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


async def get_test_session():
    async with async_test_session_maker() as session:
        yield session


@pytest_asyncio.fixture()
async def r_client():
    """
    redis client fixture for cache management
    """
    client = redis.from_url(Config.REDIS_URL, decode_responses=True)
    yield client
    await client.aclose()


@pytest_asyncio.fixture()
async def test_session():
    """
    database sesssion fixture for database management
    """
    async with async_test_session_maker() as db:
        yield db
        await db.close()


@pytest_asyncio.fixture(scope="session")
async def test_client():
    """
    http test client fixture for CRUD API actions
    """
    async with engine.begin() as conn:
        from src.db.models import (
            User,
            Message,
            Chatroom,
            BlacklistedEmail,
            BlacklistedToken,
            UserChatroomBannedLink,
            UserChatroomLink,
            UserChatroomModeratorsLink,
            UserFriendship,
            UserFriendshipRequest,
        )

        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    app.dependency_overrides[get_session] = get_test_session

    with TestClient(app) as client:
        yield client
