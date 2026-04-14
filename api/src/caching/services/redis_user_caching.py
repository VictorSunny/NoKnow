# import json
# from logging import getLogger
# from uuid import UUID
# import redis.asyncio as redis
# from src.apps.auth.schemas.base_schemas import UserCache
# from src.configurations.config import Config
# from src.db.models import User

# logger = getLogger(__name__)

# async def set_user_cache(user: User, r_client: redis.Redis):
#     user_data = json.loads(user.model_dump_json(exclude_none=True))
#     await  r_client.hset(name=Config.REDIS_USER_NAME_PREFIX, key=str(user.uid), mapping=user_data)
#     logger.info(f"successfully set cache for user with id: {user.uid}")

# async def get_user_from_cache(id: UUID, r_client: redis.Redis):
#     user_cache = None
#     redis_res = await r_client.hgetall(Config.REDIS_USER_NAME_PREFIX, str(id))
#     if redis_res:
#         user_cache = UserCache(**redis_res)
#         logger.info(f"successfully retrieved cache for user with id: {id}")
