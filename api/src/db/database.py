from logging import getLogger
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, DBAPIError
from sqlmodel import SQLModel

import redis.asyncio as redis

from src.configurations.config import ASYNC_DATABASE_URL, Config
from src.exceptions.http_exceptions import http_raise_server_unavailable

logger = getLogger(__name__)


### IMPORT SENSITIVE ENVIRONMENT VARIABLES
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async_session_maker = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session():
    logger.info("db session started")
    try:
        async with async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                raise
            finally:
                await session.close()
    except OSError:
        await session.rollback()
        http_raise_server_unavailable(reason="Database server unavailable.")
    except DBAPIError:
        await session.rollback()
        raise
    finally:
        logger.info("db session closed")

async def get_redis_session():
    try:
        logger.info("starting redis session")
        async with redis.from_url(Config.REDIS_URL) as redis_client:
            try:
                yield redis_client
            finally:
                await redis_client.aclose()
    finally:
        logger.info("redis session closed")
