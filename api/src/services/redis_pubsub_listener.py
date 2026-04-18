

import ast
import asyncio
from logging import getLogger

from redis import RedisError
from src.services.websocket_manager import ws_manager
import redis.asyncio as redis
from redis.asyncio.client import PubSub

logger = getLogger(__name__)

async def redis_pubsub_listener(r_client: redis.Redis, pubsub: PubSub):
    try:
        await r_client.ping()
        logger.info("successfully started pubsub listener")
        while True:
            message_json = await pubsub.get_message(timeout=1.0, ignore_subscribe_messages=True)
            if message_json:
                # if message_json:
                print("new message in listener", message_json)
                message_channel_id = message_json["channel"].split(":")[1]
                message_data = message_json["data"]
                if (
                    (type(message_data) == str)
                    and (message_data[0] == "{")
                    and (message_data[-1] == "}")
                ):
                    message_data = ast.literal_eval(message_data)
                    await ws_manager.broadcast(
                        id=message_channel_id, message_json=message_data
                        )
            await asyncio.sleep(0.02)
    except RedisError:
        logger.info("stopped pubsub listener")
        pass
    except asyncio.CancelledError:
        logger.info("stopped pubsub listener")
        raise