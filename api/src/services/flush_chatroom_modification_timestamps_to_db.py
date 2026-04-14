import asyncio
from logging import getLogger
from uuid import UUID

from fastapi import FastAPI

from regex import P
from sqlalchemy import update
from src.db.models import Chatroom
from src.db.database import async_session_maker

from src.configurations.config import Config

logger = getLogger(__name__)

async def flush_chatroom_modification_timestamps_to_db(app: FastAPI):
    r_client = app.state.r_client
    while True:
        queued_modification_timestamps = await r_client.hgetall(Config.REDIS_CHATROOM_MODIFICATION_DATE_LIST_NAME)
        queue_length = len(queued_modification_timestamps)
        if queue_length > 0:
            logger.info(f"flushing {queue_length} modification_timestamps from redis to database")
            async with async_session_maker() as db:
                for key, value in queued_modification_timestamps.items():
                    query = update(Chatroom).where(Chatroom.uid == UUID(key)).values(modified_at=float(value))
                    await r_client.hdel(Config.REDIS_CHATROOM_MODIFICATION_DATE_LIST_NAME, key)
                    await db.execute(query)
                await db.commit()
                await db.close()
        await asyncio.sleep(60)