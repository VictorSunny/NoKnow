import ast
import asyncio
from logging import getLogger

from fastapi import FastAPI
from src.db.models import Message
from src.db.database import async_session_maker


from src.configurations.config import Config

logger = getLogger(__name__)


async def flush_messages_to_db(app: FastAPI):
    r_client = app.state.r_client
    while True:
        queued_messages_length = await r_client.llen(Config.REDIS_MESSAGE_LIST)
        if (queued_messages_length) and (int(queued_messages_length) > 0):
            message_batch = await r_client.lpop(Config.REDIS_MESSAGE_LIST, 200)
            logger.info(
                f"flushing {queued_messages_length} messages from redis to database"
            )
            async with async_session_maker() as db:
                for message in message_batch:
                    parsed_message = ast.literal_eval(message)
                    new_message = Message(**parsed_message)
                    db.add(new_message)
                await db.commit()
                await db.close()
        await asyncio.sleep(0.3)
