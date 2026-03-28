from datetime import datetime, timedelta
from pydantic import EmailStr
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select, func, exists

from src.apps.auth.schemas.base_schemas import BlacklistedEmailCreate
from src.apps.admin.schemas.admin_base_schemas import FromDate, RawBlacklistedEmailList
from src.db.models import BlacklistedEmail
from src.exceptions.http_exceptions import (
    http_raise_not_found,
    http_raise_unprocessable_entity,
)
from src.generics.schemas import MessageResponse, SortByDateOrID, SortOrder
from src.utilities.utilities import offset_by_page, utc_time_now, validate_int_list


async def check_email_in_blacklist(email: EmailStr, db: AsyncSession):
    """
    Checks `email`s exists in blacklist.
    Returns `True` value if email exists, else, returns `False`.

    Args:
        email: String (valid email address) for finding `BlacklistedEmail`
        db: Asynchronous database connection instance
    """
    query = select(
        exists().where(
            func.lower(BlacklistedEmail.sub) == email.lower(),
        )
    )
    executed_query = await db.execute(query)
    email_exists = executed_query.scalar_one()
    return email_exists


async def get_user_blacklisted_email(id: int, db: AsyncSession) -> BlacklistedEmail:
    """
    Returns `BlacklistedEmail`.

    Args:
        id: Int identifier for `BlacklistedEmail` to be returned
        db: Asynchronous database connection instance
    """
    blacklisted_email = await db.get(BlacklistedEmail, id)
    if not blacklisted_email:
        http_raise_not_found(reason="No existing blacklisted email with matching ID.")
    return blacklisted_email


async def create_blacklisted_email(
    json: BlacklistedEmailCreate, db: AsyncSession
) -> BlacklistedEmail:
    """
    Creates a new `BlacklistedEmail`.

    Args:
        json: Creation data
        db: Asynchronous database connection instance
    """
    new_blacklisted_email = BlacklistedEmail(**json.model_dump())
    db.add(new_blacklisted_email)
    await db.commit()
    await db.refresh(new_blacklisted_email)

    return new_blacklisted_email


async def update_blacklisted_email(
    id: int, json: BlacklistedEmailCreate, db: AsyncSession
) -> BlacklistedEmail:
    """
    Updates `BlacklistedEmail`.

    Args:
        id: Int identifier for `BlacklistedEmail` to be updated
        json: Update data
        db: Asynchronous database connection instance
    """
    blacklisted_email = await db.get(BlacklistedEmail, id)
    if not blacklisted_email:
        http_raise_not_found(reason="No matching blacklisted email found to update.")

    new_email = json.sub
    if new_email == blacklisted_email.sub:
        http_raise_unprocessable_entity(reason="No changes detected.")
    blacklisted_email.sub = new_email
    db.add(blacklisted_email)
    await db.commit()
    await db.refresh(blacklisted_email)

    return blacklisted_email


async def get_all_blacklisted_user_emails(
    page: int,
    sort: SortByDateOrID,
    order: SortOrder,
    from_date: FromDate,
    search_query: str | None,
    db: AsyncSession,
) -> RawBlacklistedEmailList:
    """
    Returns blacklisted emails in database.

    Args:
        page: Int value for offsetting rows to be retrieved
            user: Logged in `User` instance
            sort: String value for what rows are to be arranged by
            order: Direction of arrangement of rows
            from_date: String value indicating minimum allowed recency for rows to be retrieved
            search_query: String value for finding matching `BlacklistedEmail`s
            db: Asynchronous database connection instance
    """
    limit = 50
    offset = offset_by_page(page_num=page, limit=limit)
    query = select(BlacklistedEmail).limit(limit).offset(offset)

    if sort == SortByDateOrID.ID:
        query = query.order_by(
            BlacklistedEmail.id.asc()
            if order == SortOrder.ASC
            else BlacklistedEmail.id.desc()
        )

    if sort == SortByDateOrID.DATE:
        query = query.order_by(
            BlacklistedEmail.created_at.asc()
            if order == SortOrder.ASC
            else BlacklistedEmail.created_at.desc()
        )

    current_time = utc_time_now()
    if from_date == FromDate.ONE_DAY:
        past_day: datetime = current_time - timedelta(days=1)
        past_day_stamp = past_day.timestamp()
        query = query.where(BlacklistedEmail.created_at >= past_day_stamp)
    # past week
    if from_date == FromDate.ONE_WEEK:
        past_week: datetime = current_time - timedelta(days=7)
        past_week_stamp = past_week.timestamp()
        query = query.where(BlacklistedEmail.created_at >= past_week_stamp)
    # past month
    if from_date == FromDate.ONE_MONTH:
        past_month: datetime = current_time - timedelta(days=30)
        past_month_stamp = past_month.timestamp()
        query = query.where(BlacklistedEmail.created_at >= past_month_stamp)
    # past 3 months
    if from_date == FromDate.THREE_MONTHS:
        past_three_months: datetime = current_time - timedelta(days=30 * 3)
        past_three_months_stamp = past_three_months.timestamp()
        query = query.where(BlacklistedEmail.created_at >= past_three_months_stamp)
    # past 6 months
    if from_date == FromDate.SIX_MONTHS:
        past_six_months: datetime = current_time - timedelta(days=30 * 6)
        past_six_months_stamp = past_six_months.timestamp()
        query = query.where(BlacklistedEmail.created_at >= past_six_months_stamp)
    # past year
    if from_date == FromDate.ONE_YEAR:
        past_year: datetime = current_time - timedelta(weeks=52)
        past_year_stamp = past_year.timestamp()
        query = query.where(BlacklistedEmail.created_at >= past_year_stamp)

    executed_query = await db.execute(query)
    email_blacklist = executed_query.unique().scalars().all()
    response = {"emails": email_blacklist}
    return response


async def add_email_to_blacklist(email: EmailStr, db: AsyncSession) -> MessageResponse:
    """
    Blacklists user email.
    This funtion must never be used in routes.
    `User` email must only be added to email blacklist when a user account is deleted by an admin.

    Args:
        email: String value (valid email address) for creating `BlacklistedEmail`
        db: Asynchronous database connection instance
    """
    new_blacklisted_email = BlacklistedEmail(sub=email)

    db.add(new_blacklisted_email)
    await db.commit()
    await db.refresh(new_blacklisted_email)

    return {"message": f"Successfully added {new_blacklisted_email.sub} to blacklist."}


async def delete_blacklisted_user_emails(id: str, db: AsyncSession) -> MessageResponse:
    """
    Mass deletes `BlacklistedEmail`s from database,
    Allowing email to be acceptable for usersignup.

    Args:
        id: Comma seperated string list of `id`s for querying `BlacklistedEmail`s to be deleted
        db: Asynchronous database connection instance

    Raises:
        HTTPExcpetion 404: Not a single `BlacklistedEmail` was found
    """
    id_list = await validate_int_list(int_string=id, model_name="blacklisted_email")
    affected_rows = 0

    query = select(BlacklistedEmail).where(BlacklistedEmail.id.in_(id_list))
    executed_query = await db.execute(query)
    email_blacklist = executed_query.unique().scalars().all()
    if not email_blacklist:
        http_raise_not_found(
            reason="No matching blacklisted email was found to delete."
        )

    for email in email_blacklist:
        await db.delete(email)
        affected_rows += 1

    await db.commit()
    return {"message": f"Successully deleted {affected_rows} emails from blacklist."}
