import os
from pathlib import Path
from pydantic import EmailStr
from src.utilities.utilities import unslugify_string
from src.apps.auth.schemas.base_schemas import OTPType
from src.configurations.apps_config.config import Config

import smtplib
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"

template_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

MAIL_USERNAME = Config.MAIL_USERNAME
MAIL_FROM = Config.MAIL_FROM
MAIL_PASSWORD = Config.MAIL_PASSWORD
MAIL_SERVER = Config.MAIL_SERVER
MAIL_PORT = 587


def send_verification_mail(
    recipient: EmailStr, otp_code: int, verification_type: OTPType
):
    ver_type = unslugify_string(slug=verification_type)
    subject = f"Noknow {ver_type} OTP verification."
    template_body = {
        "sub": recipient,
        "otp_code": otp_code,
        "verification_type": ver_type.title(),
    }

    message_template = template_env.get_template("OTP.html")
    message_html_body = message_template.render(**template_body)

    message = EmailMessage()
    message["From"] = Config.MAIL_FROM
    message["To"] = (recipient,)
    message["Subject"] = subject
    message.set_content(message_html_body, subtype="html")

    with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as email_server:
        email_server.starttls()
        email_server.login(MAIL_USERNAME, MAIL_PASSWORD)
        email_server.send_message(message)

    return True
