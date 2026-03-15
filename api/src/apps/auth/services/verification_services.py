import re
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select, func

from src.generics.schemas import MessageResponse
from src.db.models import BlacklistedEmail, User
from src.exceptions.http_exceptions import (
    http_raise_conflict,
    http_raise_forbidden,
)


# USER DETAILS VERIFICATION FUNCTIONS -------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------
async def error_if_username_in_db(username: str, db: AsyncSession):
    """
    Raise error if `User` with matching `username` exists in the database.
    """
    query = select(User).where(func.lower(User.username) == username.lower())
    query_result = await db.execute(query)

    username_user = query_result.scalar_one_or_none()
    if username_user:
        # raise error if `User` with username already exists
        http_raise_conflict(reason="User with username already exists.")
    return


async def error_if_email_in_db(email: str, db: AsyncSession):
    """
    Raise error if `User` with matching `email` exists in the database.
    """
    email_user_query = select(User).where(func.lower(User.email) == email.lower())
    email_user_query_result = await db.execute(email_user_query)
    email_user = email_user_query_result.scalar_one_or_none()

    blacklisted_email_query = select(BlacklistedEmail).where(
        func.lower(BlacklistedEmail.sub) == email.lower()
    )
    blacklisted_email_query_result = await db.execute(blacklisted_email_query)
    blacklisted_email = blacklisted_email_query_result.scalar_one_or_none()

    if blacklisted_email:
        http_raise_forbidden(reason="This account has been banned.")
    if email_user:
        # raise error if `User` with email already exists
        http_raise_conflict(
            reason="Email already attached to an exisiting user account."
        )
    return


async def check_user_data_is_acceptable(
    email: str, username: str, db: AsyncSession
) -> MessageResponse:
    """
    Raise error if `User` with matching `email` or `username` exists in the database,
    Raise error if `email` has been blacklisted.
    """
    await error_if_email_in_db(email=email, db=db)
    await error_if_username_in_db(username=username, db=db)

    return {"message": "Data is okay."}


# -------------------------------------------------------------------------------------------------------
# END OF USER DETAILS VERIFICATION FUNCTIONS ------------------------------------------------------------
