from logging import getLogger
from fastapi import Request
from redis import RedisError
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, DBAPIError

from src.configurations.config import ASYNC_DATABASE_URL, DATABASE_URL
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

async def get_redis_session(request: Request):
    try:
        r_client = request.app.state.r_client
        connected = await r_client.ping()
        if not connected:
            raise RedisError()
        logger.info("redis connection retrieved")
        return r_client
    except Exception as e:
        raise e
