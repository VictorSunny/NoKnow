from logging import getLogger
from typing import List
from celery import Celery
import multiprocessing
import platform

from pydantic import BaseModel, EmailStr

from src.services.mail import send_verification_mail
from src.apps.auth.schemas.base_schemas import OTPType

system_is_windows = str(platform.system()).lower() == "windows"

if system_is_windows:
    multiprocessing.set_start_method("spawn", True)

logger = getLogger(__name__)

celery_app = Celery()
celery_app.config_from_object("src.configurations.apps_config.config")

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
