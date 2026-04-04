from logging import getLogger
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, DBAPIError
import redis.asyncio as redis

from src.configurations.config import ASYNC_DATABASE_URL, DATABASE_URL, Config
from src.exceptions.http_exceptions import http_raise_service_unavailable

logger = getLogger(__name__)


sync_engine = create_engine(DATABASE_URL, echo=False)
sync_session_maker = sessionmaker(
    sync_engine, class_=Session, expire_on_commit=False, autoflush=False
)
def get_sync_session():
    logger.info("sync db session started")
    try:
        with sync_session_maker() as session:
            try:
                yield session
                session.commit()
            except SQLAlchemyError:
                session.rollback()
                raise
            finally:
                session.close()
    except OSError:
        session.rollback()
        http_raise_service_unavailable(reason="Database server unavailable.")
    except DBAPIError:
        session.rollback()
        raise
    finally:
        logger.info("db session closed")
        

async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
async_session_maker = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)
async def get_session():
    logger.info("async db session started")
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
        http_raise_service_unavailable(reason="Database server unavailable.")
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
