from logging import getLogger
from celery import Celery
import multiprocessing
import platform

from pydantic import EmailStr
from redis import Redis
from redis.exceptions import ConnectionError, TimeoutError
from redis.retry import Retry
from redis.backoff import ExponentialWithJitterBackoff

from src.configurations.config import Config
from src.services.send_verification_mail import send_verification_mail
from src.apps.auth.schemas.base_schemas import OTPType

system_is_windows = str(platform.system()).lower() == "windows"

if system_is_windows:
    multiprocessing.set_start_method("spawn", True)

logger = getLogger(__name__)

celery_app = Celery()
celery_app.config_from_object("src.configurations.config")

r_client = Redis.from_url(
    url=Config.REDIS_URL,
    decode_responses=True,
    retry_on_error=[ConnectionError, TimeoutError],
    retry=Retry(
        ExponentialWithJitterBackoff(cap=4, base=1),
        retries=5
    ),
)
if system_is_windows:
    celery_app.conf.update(
        worker_pool="solo", task_track_started=True, timezone="UTC", enable_utc=True
    )

@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=8,
    retry_backoff=True,
    retry_backoff_max=120,
    retry_jitter=True,
)
def send_user_otp_email(
    self, recipient: EmailStr, verification_type: OTPType, otp_code: int
):
    logger.info(f"sending {verification_type} email verification to: {recipient}")
    try:
        send_verification_mail(
            recipient=recipient, otp_code=otp_code, verification_type=verification_type
        )
        logger.info(
            f"successfully sent {verification_type} email verification to: {recipient}"
        )
    except Exception as exc:
        retries_left = self.max_retries - self.request.retries
        if retries_left > 0:
            raise self.retry(exc=exc)
        logger.error(exc)
    