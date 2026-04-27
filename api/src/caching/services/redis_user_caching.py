import json
from logging import getLogger
from uuid import UUID
import redis.asyncio as redis
from src.caching.schemas.user_cache_schemas import UserCache
from src.configurations.config import Config
from src.db.models import User

logger = getLogger(__name__)


async def clear_user_cache(user: User, r_client: redis.Redis):
    logger.info("clearing cache for user", user.uid)

    uid_key = f"{Config.REDIS_USER_NAME_PREFIX}:{str(user.uid)}"
    email_key = f"{Config.REDIS_USER_NAME_PREFIX}:{user.email}"
    username_key = f"{Config.REDIS_USER_NAME_PREFIX}:{user.username}"

    await r_client.delete(uid_key)
    await r_client.delete(email_key)
    await r_client.delete(username_key)


async def set_user_cache(user: User, r_client: redis.Redis):
    await clear_user_cache(user=user, r_client=r_client)

    logger.info("setting cache for user", user.uid)
    
    user_data = json.loads(user.model_dump_json(exclude_none=True))
    user_data = {key: str(value) for key, value in user_data.items()}

    uid_key = f"{Config.REDIS_USER_NAME_PREFIX}:{str(user.uid)}"
    email_key = f"{Config.REDIS_USER_NAME_PREFIX}:{user.email}"
    username_key = f"{Config.REDIS_USER_NAME_PREFIX}:{user.username}"

    await r_client.hset(uid_key, mapping=user_data)
    await r_client.hset(username_key, mapping=user_data)
    await r_client.hset(email_key, mapping=user_data)

    logger.info(f"successfully set cache for user with id: {user.uid}")


async def get_user_from_cache(id: UUID | str, r_client: redis.Redis):
    user_cache = None
    redis_res = await r_client.hgetall(f"{Config.REDIS_USER_NAME_PREFIX}:{str(id)}")
    if redis_res:
        user_cache = UserCache(**redis_res)
        logger.info(f"successfully retrieved cache for user with identifier: {id}")
    return user_cache
