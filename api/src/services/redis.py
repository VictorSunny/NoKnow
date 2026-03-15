from enum import Enum
from logging import getLogger
import redis.asyncio as redis
from src.exceptions.http_exceptions import http_raise_forbidden
from src.utilities.utilities import (
    bytes_to_dict,
    slugify_strings,
    utc_time_now,
)
from src.configurations.apps_config.config import Config
from src.apps.auth.schemas.base_schemas import OTPType

logger = getLogger(__name__)


async def get_otp_from_cache(sub: str, otp_type: OTPType, r_client: redis.Redis):
    key = slugify_strings([sub, otp_type])
    token_bytes = await r_client.get(name=key)
    if not token_bytes:
        http_raise_forbidden(reason="Please request for a new OTP.")
    token = bytes_to_dict(token_bytes)
    return token


async def clear_otp_from_cache(sub: str, otp_type: OTPType, r_client: redis.Redis):
    key = slugify_strings([sub, otp_type])
    await r_client.delete(key)
    return {"message": "success"}


async def store_otp_code_to_cache(
    sub: str, otp_type: OTPType, code: int, r_client: redis.Redis
):
    key = slugify_strings([sub, otp_type])
    expiry = utc_time_now(exp=60)
    otp_data = {
        "sub": sub,
        "otp_type": otp_type.value,
        "code": code,
        "exp": str(expiry),
    }
    await r_client.set(name=key, value=str(otp_data), ex=60 * 2)

    logger.info(f"success. {otp_type} otp data stored for sub: {sub}.")
    return {"message": "success"}
