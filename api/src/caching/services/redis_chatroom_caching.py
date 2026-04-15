import json
from logging import getLogger
from uuid import UUID
import redis.asyncio as redis
from src.caching.schemas.chat_cache_schemas import ChatroomCache
from src.configurations.config import Config
from src.db.models import Chatroom
from src.utilities.utilities import (
    timestamp_now,
)

logger = getLogger(__name__)

async def set_chatroom_modified_at_cache(id: UUID, r_client: redis.Redis):
    # fix hash key
    await r_client.hset(Config.REDIS_CHATROOM_MODIFICATION_DATE_LIST_NAME, str(id), str(timestamp_now()))
    logger.info(f"added modification time to cache list for chatroom with id: {id}")
    
async def activate_chatroom_secret_mode(id: UUID, r_client: redis.Redis):
    await r_client.sadd(Config.REDIS_SECRET_CHATROOMS_LIST_NAME, str(id))
    logger.info(f"activated secret mode status cache for chatroom with id: {id}")
async def deactivate_chatroom_secret_mode(id: UUID, r_client: redis.Redis):
    await r_client.srem(Config.REDIS_SECRET_CHATROOMS_LIST_NAME, str(id))
    logger.info(f"deactivated secret mode status cache for chatroom with id: {id}")
async def check_chatroom_secret_mode_active(id: UUID, r_client: redis.Redis):
    chatroom_is_secret = await r_client.sismember(Config.REDIS_SECRET_CHATROOMS_LIST_NAME, str(id))
    if chatroom_is_secret:
        return True
    return False
async def check_record_message(id: UUID, r_client: redis.Redis):
    chatroom_is_secret = await check_chatroom_secret_mode_active(id=id, r_client=r_client)
    if chatroom_is_secret:
        return False
    return True

async def set_chatroom_cache(chatroom: Chatroom, r_client: redis.Redis):
    """
    Sets cache for chatroom.
    
    Args:
        chatroom: Chatroom instance
        r_client: redis client instance
    """
    data = json.loads(chatroom.model_dump_json(exclude_none=True))
    await r_client.delete(f"{Config.REDIS_CHATROOM_NAME_PREFIX}:{str(chatroom.uid)}")
    await r_client.hset(f"{Config.REDIS_CHATROOM_NAME_PREFIX}:{str(chatroom.uid)}", mapping=data)
    logger.info(f"succesfully set cache for chatroom with id: {chatroom.uid}")
    
async def get_chatroom_from_cache(chatroom_identifier: UUID | str, r_client: redis.Redis):
    """
    Gets cache for chatroom.
    
    Args:
        chatroom_identifier: UUID/str - identifier for matching chatroom
        r_client: redis client instance
    """
    print("cache hit")
    cached_chatroom = None 
    redis_res = await r_client.hgetall(f"{Config.REDIS_CHATROOM_NAME_PREFIX}:{str(chatroom_identifier)}")
    if redis_res:
        cached_chatroom = ChatroomCache(**redis_res)
        logger.info(f"succesfully retrieved cache for chatroom with identifier: {chatroom_identifier}")
        print(redis_res)
    return cached_chatroom

async def clear_chatroom_cache(id: UUID, r_client: redis.Redis):
    await r_client.delete(f"{Config.REDIS_CHATROOM_NAME_PREFIX}:{str(id)}")
    logger.info(f"succesfully cleared cache for chatroom with id: {id}")