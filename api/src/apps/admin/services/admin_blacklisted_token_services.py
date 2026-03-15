from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select

from src.apps.admin.schemas.admin_base_schemas import FromDate, RawBlacklistedTokenList
from src.apps.admin.schemas.admin_blacklisted_token_schemas import TokenValidity
from src.db.models import BlacklistedToken
from src.exceptions.http_exceptions import (
    http_raise_not_found,
    http_raise_unprocessable_entity,
)
from src.generics.schemas import MessageResponse, SortByDateOrID, SortOrder
from src.utilities.utilities import (
    offset_by_page,
    timestamp_now,
    utc_time_now,
    validate_int_list,
)


async def get_user_blacklisted_token(id: int, db: AsyncSession) -> BlacklistedToken:
    """
    Returns `BlacklistedToken`.

    Args:
        id: Int identifier for `BlacklistedToken`
        db: Asynchronous database connection instance
    """
    blacklisted_token = await db.get(BlacklistedToken, id)
    if not blacklisted_token:
        http_raise_not_found(reason="No existing blacklisted token with matching ID.")
    return blacklisted_token


async def get_all_blacklisted_user_tokens(
    db: AsyncSession,
    page: int,
    sort: SortByDateOrID,
    order: SortOrder,
    validity: TokenValidity,
    from_date: FromDate,
) -> RawBlacklistedTokenList:
    """
    Returns `BlacklistedToken`s in database.

    Args:
        page: Int value for offsetting rows to be retrieved
            sort: String value for what rows are to be arranged by
            order: Direction of arrangement of rows
            from_date: String value indicating minimum allowed recency for rows to be retrieved
            db: Asynchronous database connection instance
    """
    limit = 50
    offset = offset_by_page(page_num=page, limit=limit)
    query = select(BlacklistedToken).limit(limit).offset(offset)
    if sort == SortByDateOrID.ID:
        query = query.order_by(
            BlacklistedToken.id.asc()
            if order == SortOrder.ASC
            else BlacklistedToken.id.desc()
        )

    if sort == SortByDateOrID.DATE:
        query = query.order_by(
            BlacklistedToken.created_at.asc()
            if order == SortOrder.ASC
            else BlacklistedToken.created_at.desc()
        )

    # filter by validity
    if validity != TokenValidity.ALL:
        current_timestamp = timestamp_now()
        # get only expired tokens
        if validity == TokenValidity.EXPIRED:
            query = query.where(BlacklistedToken.exp < current_timestamp)
        # get only fresh tokens
        if validity == TokenValidity.FRESH:
            query = query.where(BlacklistedToken.exp > current_timestamp)

    current_time = utc_time_now()
    # past day
    if from_date == FromDate.ONE_DAY:
        past_day: datetime = current_time - timedelta(days=1)
        past_day_stamp = past_day.timestamp()
        query = query.where(BlacklistedToken.created_at >= past_day_stamp)
    # past week
    if from_date == FromDate.ONE_WEEK:
        past_week: datetime = current_time - timedelta(days=7)
        past_week_stamp = past_week.timestamp()
        query = query.where(BlacklistedToken.created_at >= past_week_stamp)
    # past month
    if from_date == FromDate.ONE_MONTH:
        past_month: datetime = current_time - timedelta(days=30)
        past_month_stamp = past_month.timestamp()
        query = query.where(BlacklistedToken.created_at >= past_month_stamp)
    # past 3 months
    if from_date == FromDate.THREE_MONTHS:
        past_three_months: datetime = current_time - timedelta(days=30 * 3)
        past_three_months_stamp = past_three_months.timestamp()
        query = query.where(BlacklistedToken.created_at >= past_three_months_stamp)
    # past 6 months
    if from_date == FromDate.SIX_MONTHS:
        past_six_months: datetime = current_time - timedelta(days=30 * 6)
        past_six_months_stamp = past_six_months.timestamp()
        query = query.where(BlacklistedToken.created_at >= past_six_months_stamp)
    # past year
    if from_date == FromDate.ONE_YEAR:
        past_year: datetime = current_time - timedelta(weeks=52)
        past_year_stamp = past_year.timestamp()
        query = query.where(BlacklistedToken.created_at >= past_year_stamp)

    executed_query = await db.execute(query)
    token_blacklist = executed_query.unique().scalars().all()
    response = {"tokens": token_blacklist}
    return response


async def delete_blacklisted_user_tokens(id: str, db: AsyncSession) -> MessageResponse:
    """
    Mass delete blacklisted tokens from database.

    Args:
        id: Comma seperated string list of `id`s for querying `User`s to be added to `admin` group
        db: Asynchronous database connection instance

    Raises:
        HTTPException 422: One or more queried `BlacklistedToken`s to be deleted is not yet expired.
            Only expired tokens should be deleted.
    """
    id_list = await validate_int_list(int_string=id, model_name="blacklisted_token")
    affected_rows = 0

    query = select(BlacklistedToken).where(BlacklistedToken.id.in_(id_list))
    executed_query = await db.execute(query)
    token_blacklist = executed_query.unique().scalars().all()
    if not token_blacklist:
        http_raise_not_found(
            reason="No matching blacklisted token was found to delete."
        )

    current_timestamp = timestamp_now()
    for token in token_blacklist:
        # raise error if any queried token is not yet expired
        # this prevents security violations
        if token.exp > current_timestamp:
            http_raise_unprocessable_entity(
                reason="Only expired blacklisted tokens can be deleted."
            )
        await db.delete(token)
        affected_rows += 1

    await db.commit()

    return {"message": f"Successully deleted {affected_rows} tokens from blacklist."}
