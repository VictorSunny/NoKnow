from datetime import datetime, timedelta
from sqlmodel import select

import redis.asyncio as redis

from src.caching.services.redis_chatroom_caching import clear_chatroom_cache
from src.apps.user.services.base_services import get_user_by_username
from src.apps.admin.schemas.admin_base_schemas import FromDate
from src.apps.chat.schemas.base_schemas import (
    AdminChatroomCreateForm,
    ChatroomPrivatePublicType,
    ChatroomType,
    ChatroomsSort,
    RawChatroomList,
)
from src.db.models import Chatroom, User, UserChatroomLink, UserChatroomModeratorsLink
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.exceptions.http_exceptions import (
    http_raise_not_found,
    http_raise_unprocessable_entity,
)
from src.generics.schemas import MessageResponse, SortOrder
from src.utilities.utilities import (
    hash_password,
    offset_by_page,
    utc_time_now,
    validate_uid_list,
)


async def admin_create_chatroom(
    json: AdminChatroomCreateForm, db: AsyncSession, r_client: redis.Redis
) -> Chatroom:
    """
    Creates and returns new `Chatroom`.

    Args:
        json: Creation data
        db: Asynchronous database connection instance

    Raises:
        HTTPException 422: `password` value was provided and `room_type` value is not "private".
            Only private `Chatroom`s can be password protected.
    """
    if (json.room_type != ChatroomType.PRIVATE) and (
        (json.password) or (str(json.password).strip() == "")
    ):
        http_raise_unprocessable_entity(
            reason="Only private chatrooms can be password protected."
        )

    new_chatroom = Chatroom(**json.model_dump())
    # set hashed password
    if json.password:
        hashed_password = hash_password(password=json.password)
        new_chatroom.password = hashed_password

    # set creator by value passed into form
    # raise error if user does not exist
    creator = await get_user_by_username(
        username=json.original_creator_username, db=db, r_client=r_client
    )
    new_chatroom.creator_uid = creator.uid

    db.add(new_chatroom)
    await db.commit()
    await db.refresh(new_chatroom)

    new_chatroom.members_count = 1
    new_member_link = UserChatroomLink(
        user_uid=creator.uid, chatroom_uid=new_chatroom.uid
    )

    new_moderator_link = UserChatroomModeratorsLink(
        user_uid=creator.uid, chatroom_uid=new_chatroom.uid
    )

    db.add(new_member_link)
    db.add(new_moderator_link)
    await db.commit()

    return new_chatroom


async def get_all_created_chatrooms(
    room_type: ChatroomPrivatePublicType,
    page: int,
    sort: ChatroomsSort,
    order: SortOrder,
    from_date: FromDate,
    min_members: int,
    search_query: str | None,
    db: AsyncSession,
) -> RawChatroomList:
    """
    Returns all `Chatroom`s that are not "personal" i.e between friends.

    Args:
        room_type: String value for type of `Chatroom` to be returned e.g "public", "private"
        page: Int value for offsetting rows to be retrieved
        sort: String value for what rows are to be arranged by
        order: Direction of arrangement of rows
        from_date: String value indicating minimum allowed recency for rows to be retrieved
        min_members: Int value for minimum number of members a `Chatroom` must have to be retrieved for return
        search_query: String value for finding matching `Chatroom`s
        db: Asynchronous database connection instance
    """
    if min_members < 0:
        http_raise_unprocessable_entity(
            reason="Min members value must be greater than 0."
        )

    limit = 50
    offset = offset_by_page(page_num=page, limit=limit)
    query = (
        select(Chatroom)
        .limit(limit)
        .offset(offset)
        .where(Chatroom.members_count >= min_members)
        .where(Chatroom.room_type != ChatroomType.PERSONAL)
    )
    if room_type != ChatroomPrivatePublicType.ALL:
        query = query.where(Chatroom.room_type == room_type)
    if sort == ChatroomsSort.NAME:
        query = query.order_by(
            Chatroom.name.asc() if order == SortOrder.ASC else Chatroom.name.desc()
        )

    if sort == ChatroomsSort.DATE:
        query = query.order_by(
            Chatroom.created_at.asc()
            if order == SortOrder.ASC
            else Chatroom.created_at.desc()
        )

    if sort == ChatroomsSort.ACTIVITY:
        query = query.order_by(
            Chatroom.modified_at.asc()
            if order == SortOrder.ASC
            else Chatroom.modified_at.desc()
        )

    if sort == ChatroomsSort.POPULARITY:
        query = query.order_by(
            Chatroom.members_count.asc()
            if order == SortOrder.ASC
            else Chatroom.members_count.desc()
        )

    current_time = utc_time_now()
    # past day
    if from_date == FromDate.ONE_DAY:
        past_day: datetime = current_time - timedelta(days=1)
        past_day_stamp = past_day.timestamp()
        query = query.where(Chatroom.created_at >= past_day_stamp)
    # past week
    if from_date == FromDate.ONE_WEEK:
        past_week: datetime = current_time - timedelta(days=7)
        past_week_stamp = past_week.timestamp()
        query = query.where(Chatroom.created_at >= past_week_stamp)
    # past month
    if from_date == FromDate.ONE_MONTH:
        past_month: datetime = current_time - timedelta(days=30)
        past_month_stamp = past_month.timestamp()
        query = query.where(Chatroom.created_at >= past_month_stamp)
    # past 3 months
    if from_date == FromDate.THREE_MONTHS:
        past_three_months: datetime = current_time - timedelta(days=30 * 3)
        past_three_months_stamp = past_three_months.timestamp()
        query = query.where(Chatroom.created_at >= past_three_months_stamp)
    # past 6 months
    if from_date == FromDate.SIX_MONTHS:
        past_six_months: datetime = current_time - timedelta(days=30 * 6)
        past_six_months_stamp = past_six_months.timestamp()
        query = query.where(Chatroom.created_at >= past_six_months_stamp)
    # past year
    if from_date == FromDate.ONE_YEAR:
        past_year: datetime = current_time - timedelta(weeks=52)
        past_year_stamp = past_year.timestamp()
        query = query.where(Chatroom.created_at >= past_year_stamp)

    executed_query = await db.execute(query)
    email_blacklist = executed_query.unique().scalars().all()
    response = {"chatrooms": email_blacklist}
    return response


async def mass_delete_chatrooms(
    id: str, db: AsyncSession, r_client: redis.Redis
) -> MessageResponse:
    """
    Deletes multiple queried `Chatroom`s.

    Args:
        id: Comma seperated string list of `id`s for querying `Chatroom`s to be deleted.
        db: Asynchronous database connection instance

    Raises:
        HTTPException 404: Not a single `Chatroom` found
    """
    uid_list = await validate_uid_list(uid_list=id, model_name="chatroom")
    affected_rows = 0

    query = select(Chatroom).where(Chatroom.uid.in_(uid_list))
    executed_query = await db.execute(query)
    chatroom_List = executed_query.unique().scalars().all()
    if not chatroom_List:
        http_raise_not_found(
            reason="No matching blacklisted email was found to delete."
        )

    for chatroom in chatroom_List:
        await clear_chatroom_cache(id=chatroom.uid, r_client=r_client)
        await db.delete(chatroom)
        affected_rows += 1

    await db.commit()

    return {"message": f"Successully deleted {affected_rows} chatrooms."}
