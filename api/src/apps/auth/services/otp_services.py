import random

from pydantic import EmailStr

from src.apps.auth.schemas.base_schemas import OTPJWTResponse, OTPType
from src.generics.schemas import MessageResponse
from src.background_tasks.celery_email_verification_task import send_user_otp_email
from src.caching.services.redis_otp_caching import (
    clear_otp_from_cache,
    get_otp_from_cache,
    store_otp_code_to_cache,
)
import redis.asyncio as redis

from src.apps.auth.services.jwt_services import (
    create_generic_jwt,
    decode_generic_jwt,
)
from src.exceptions.http_exceptions import (
    http_raise_forbidden,
    http_raise_not_found,
)
from logging import getLogger

logger = getLogger(__name__)


async def create_send_cache_otp(
    sub: str, otp_type: str, r_client: redis.Redis
) -> MessageResponse:
    """
    Creates, caches, and queues email sendin of OTP code.

    Args:
        sub: String value (expecting valid email address) to recieve OTP email
        otp_type: String value indicating use case for OTP
        r_client: Python `Redis` client instance
    """

    logger.info(f"creating {otp_type} otp for email: {sub}")

    code = random.randint(1000, 9999)
    await store_otp_code_to_cache(
        sub=sub, otp_type=otp_type, code=code, r_client=r_client
    )

    logger.info(f"queuing {otp_type} otp to be sent to email: {sub}")
    send_user_otp_email.delay(sub, otp_type, code)

    return {"message": f"Success. {otp_type} OTP sent to email: {sub}."}


async def confirm_otp_code_create_otp_jwt(
    sub: str, otp_type: str, code: str, r_client: redis.Redis
) -> OTPJWTResponse:
    """
    Retrieves OTP cache and confirms that OTP `code` is correct.
    If OTP `code` is correct, creates JWT for `otp_type` use case. e.g "email_change", "login"

    Args:
        sub: String value (expecting valid email address) associated to OTP cache
        otp_type: String value indicating use case for OTP
        code: OTP code to be confirmed
        r_client: Python `Redis` client instance

    Raises:
        HTTPException 403: OTP `code` is incorrect
        HTTPException 404: OTP cache expired, or does not exist
    """
    logger.info(f"confirming {otp_type} otp code for email {sub}")

    otp_dict = await get_otp_from_cache(sub=sub, otp_type=otp_type, r_client=r_client)
    if not otp_dict:
        http_raise_not_found(f"Please request for a new {otp_type} OTP.")
    if code == otp_dict.get("code"):
        otp_confirmation_data = {"otp_type": otp_type, "sub": sub}
        otp_jwt = await create_generic_jwt(
            json=otp_confirmation_data, token_use="otp", exp=60
        )
        await clear_otp_from_cache(sub=sub, otp_type=otp_type, r_client=r_client)

        logger.info(f"successfully confirmed {otp_type} otp code for email {sub}")
        response = {"otp_jwt": otp_jwt}
        return response
    else:
        http_raise_forbidden("Incorrect OTP. Please confirm code and retry.")


async def confirm_otp_jwt(
    token: str, expected_sub: EmailStr, expected_otp_type: OTPType
) -> EmailStr:
    """
    Confirms JWT `token` is being used in the correct (`expected_otp_type`) context,
    And that email `sub` from decoded `token` matches `expected_sub` email.

    Returns: String(Email)

    Args:
        token: String value (expecting valid email address) to recieve OTP email
        expected_sub: Expected email `sub` to be present in JWT data after decoding
        expected_otp_type: String value indicating the expected use case to be present in JWT data after decoding

    Raises:
        HTTPException:
            401: JWT Invalid.
                -JWT expired
                -JWT was not created for the `expected_otp_type`/use case.
                -JWT was not created for the `expected_sub` email.
    """
    payload = await decode_generic_jwt(token=token, token_use="otp")
    sub, token_use, otp_type = (
        payload.get("sub"),
        payload.get("token_use"),
        payload.get("otp_type"),
    )
    if (token_use != "otp") or (otp_type != expected_otp_type):
        http_raise_forbidden(
            reason=f"Invalid {expected_otp_type} OTP token. Please generate a valid {expected_otp_type} OTP token for this action."
        )
    if sub != expected_sub:
        http_raise_forbidden(
            reason="Suspicious activity detected. Please restart otp dialogue."
        )
    return sub
