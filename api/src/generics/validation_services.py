from uuid import UUID
from src.db.models import User
from src.exceptions.http_exceptions import http_raise_forbidden
from src.utilities.utilities import check_password


async def error_if_model_password_incorrect(
    password: str, model_name: str, hashed_password: str
):
    password_valid = check_password(password=password, hashed_password=hashed_password)
    if not password_valid:
        http_raise_forbidden(reason="Incorrect password.")

    return True


async def password_check_response(password: str, user: User):
    if not user.password:
        http_raise_forbidden(
            reason="User password not set. Set password with email through account recovery process."
        )
    password_check = check_password(password=password, hashed_password=user.password)
    response = {"valid": password_check}
    return response
