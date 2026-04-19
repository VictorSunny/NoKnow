from datetime import datetime, timedelta
from logging import getLogger
from urllib.parse import unquote
from uuid import UUID
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import or_, select

import redis.asyncio as redis

from src.caching.services.redis_user_caching import clear_user_cache, set_user_cache
from src.apps.user.schemas.base_schemas import (
    AdminUserSortBy,
    RawUserList,
    UserRole,
    UserRoleChoices,
)
from src.apps.admin.services.admin_blacklisted_email_services import (
    add_email_to_blacklist,
    check_email_in_blacklist,
)
from src.apps.admin.schemas.admin_base_schemas import FromDate
from src.apps.user.services.base_services import get_user_by_uid
from src.apps.auth.services.verification_services import (
    error_if_email_in_db,
    error_if_username_in_db,
)
from src.generics.schemas import MessageResponse, OptionalBooleanString, SortOrder
from src.utilities.utilities import (
    check_password,
    hash_password,
    offset_by_page,
    utc_time_now,
    validate_uid_list,
)
from src.apps.auth.schemas.base_schemas import UserUpdateComplete
from src.db.models import User
from src.exceptions.http_exceptions import (
    http_raise_forbidden,
    http_raise_not_found,
    http_raise_unprocessable_entity,
)

logger = getLogger(__name__)


async def get_all_created_users(
    user: User,
    page: int,
    sort: AdminUserSortBy,
    order: SortOrder,
    role: UserRoleChoices,
    from_date: FromDate,
    active: OptionalBooleanString,
    google_signup: OptionalBooleanString,
    search_query: str | None,
    db: AsyncSession,
) -> RawUserList:
    """
    Returns `User`s in database

    Args:
        user: Logged in `User` instance
        page: Int value for offsetting rows to be retrieved
        sort: String value for what rows are to be arranged by
        order: Direction of arrangement of rows
        from_date: String value indicating minimum allowed recency for rows to be retrieved
        role: Value for what `User` group to return e.g admin, supeuser
        active: Boolean value indicating whether to return all, restricted, or unrestricted `User`s
        google_signup: Boolean value indicating whether to return
            all, google oauth2 signed up, or `non` google oauth2 signed up `User`s
        search_query: String value for finding matching `User`s
        db: Asynchronous database connection instance
        :***
    """
    limit = 50
    offset = offset_by_page(page_num=page, limit=limit)
    query = select(User).offset(offset).limit(limit).where(User.uid != user.uid)

    # filter users by role
    if role != UserRoleChoices.ALL:
        query = query.where(User.role == role)

    # filter users by active/restricted status
    if active == OptionalBooleanString.TRUE:
        query = query.where(User.active == True)
    if active == OptionalBooleanString.FALSE:
        query = query.where(User.active == False)

    # filter users that signedup via google oauth2
    if google_signup == OptionalBooleanString.TRUE:
        query = query.where(User.google_oauth2_id != None)
    if google_signup == OptionalBooleanString.FALSE:
        query = query.where(User.google_oauth2_id == None)

    # sort users by date of creation
    if sort == AdminUserSortBy.DATE:
        query = (
            query.order_by(User.created_at.asc())
            if order == SortOrder.ASC
            else query.order_by(User.created_at.desc())
        )

    # sort users by username
    if sort == AdminUserSortBy.USERNAME:
        query = (
            query.order_by(User.username.desc())
            if order == SortOrder.DESC
            else query.order_by(User.username.asc())
        )

    # sort users by full name
    if sort == AdminUserSortBy.NAME:
        query = (
            query.order_by(
                User.first_name.asc(), User.last_name.asc(), User.created_at.asc()
            )
            if order == SortOrder.ASC
            else query.order_by(
                User.first_name.desc(), User.last_name.desc(), User.created_at.desc()
            )
        )

    # get matching users if 'search_query' is provided
    if search_query:
        search_query = unquote(search_query).split(" ")[0]
        query = query.where(
            or_(
                User.username.ilike(f"%{search_query}%"),
                User.first_name.ilike(f"%{search_query}%"),
                User.last_name.ilike(f"%{search_query}%"),
            )
        )

    # filter users by date of creation
    current_time = utc_time_now()
    # past day
    if from_date == FromDate.ONE_DAY:
        past_day: datetime = current_time - timedelta(days=1)
        past_day_stamp = past_day.timestamp()
        query = query.where(User.created_at >= past_day_stamp)
    # past week
    if from_date == FromDate.ONE_WEEK:
        past_week: datetime = current_time - timedelta(days=7)
        past_week_stamp = past_week.timestamp()
        query = query.where(User.created_at >= past_week_stamp)
    # past month
    if from_date == FromDate.ONE_MONTH:
        past_month: datetime = current_time - timedelta(days=30)
        past_month_stamp = past_month.timestamp()
        query = query.where(User.created_at >= past_month_stamp)
    # past 3 months
    if from_date == FromDate.THREE_MONTHS:
        past_three_months: datetime = current_time - timedelta(days=30 * 3)
        past_three_months_stamp = past_three_months.timestamp()
        query = query.where(User.created_at >= past_three_months_stamp)
    # past 6 months
    if from_date == FromDate.SIX_MONTHS:
        past_six_months: datetime = current_time - timedelta(days=30 * 6)
        past_six_months_stamp = past_six_months.timestamp()
        query = query.where(User.created_at >= past_six_months_stamp)
    # past year
    if from_date == FromDate.ONE_YEAR:
        past_year: datetime = current_time - timedelta(weeks=52)
        past_year_stamp = past_year.timestamp()
        query = query.where(User.created_at >= past_year_stamp)

    # execute query
    executed_query = await db.execute(query)
    user_list = executed_query.scalars().unique().all()
    response = {"users": user_list}
    return response


async def update_user_full_data(
    id: UUID,
    json: UserUpdateComplete,
    user: User,
    db: AsyncSession,
    r_client: redis.Redis
) -> User:
    """
    Updates data of `User` with matching `id`.

    Args:
        id: UUID for `User`
        json: Update data
        user: Logged in `User`
        db: Asynchronous database connection instance

    Raises:
        403:
            -Logged in `User` is not a `superuser` and `json` data contains `User` role value.
                Only `superuser` can changed a `User`'s role
            -Candidate `User` to update is a `superuser`.
                Only a `superuser` can update their own data.
        409: Update data contains field value that breaks `User` table unique constraints
        422:
            -`json` is empty
            -No changes detected between logged in `User` instance field values and `json` update data
    """

    candidate = await get_user_by_uid(id=id, db=db, r_client=r_client)
    
    print("candidate:\n", candidate.model_dump(), "update data\n", json.model_dump())

    logger.info(f"updating data for user: {candidate.uid}")

    # check if candidate to be edited is a superuser
    # if candiate is a superuser, confirm user making edit is the logged in user/account owner
    # raise error if user is not the account owner
    if (candidate.role == UserRoleChoices.SUPERUSER) and (user.uid != candidate.uid):
        http_raise_forbidden(
            reason="superuser account can be updated only by the account owner."
        )

    # check if form is fully filled and if there are changes between current candidatedata and form data
    if json.username and json.username.lower() == candidate.username.lower():
        if json.email and json.email.lower() == candidate.email.lower():
            print("same email")
            if (
                json.first_name
                and json.first_name.lower() == candidate.first_name.lower()
            ):
                print("same first name")
                if (
                    json.last_name
                    and json.last_name.lower() == candidate.last_name.lower()
                ):
                    print("same last name")
                    if json.bio and json.bio == candidate.bio:
                        print("same last bio")
                        if json.is_hidden == candidate.is_hidden:
                            print("same hidden status")
                            if json.active == candidate.active:
                                print("same active status")
                                if json.role == candidate.role:
                                    print("same role")
                                    if (candidate.password) and (not json.password):
                                        print("same password empty")
                                        http_raise_unprocessable_entity(
                                            reason="No changes detected."
                                        )
                                    elif (not candidate.password) and (not json.password):
                                        http_raise_unprocessable_entity(
                                            reason="No changes detected."
                                        )
                                    else:
                                        print("checking passwords")
                                        password_is_the_same = check_password(
                                            json.password, candidate.password
                                        )
                                        if password_is_the_same:
                                            print("same password")
                                            http_raise_unprocessable_entity(
                                                reason="No changes detected."
                                            )
                                        

    # check if candidate role is being updated
    # raise error if admin user is not a superuser as action is preserved only for superuser
    if (json.role and json.role != candidate.role) and (
        user.role != UserRoleChoices.SUPERUSER
    ):
        http_raise_forbidden(
            reason="Only a superuser is allowed to update a user's role."
        )

    # raise error if updated username exists in database already
    if json.username:
        if candidate.username.lower() != json.username.lower():
            await error_if_username_in_db(username=json.username, db=db)

    # raise error if updated email exists in database already
    if json.email:
        if candidate.email.lower() != json.email.lower():
            await error_if_email_in_db(email=json.email, db=db)

    if json.password:
        json.password = hash_password(password=json.password)

    # clear empty fields in update form to avoid clearing User object column values
    json = json.model_dump(exclude={"confirm_password"}, exclude_unset=True, exclude_none=True)
    # raise error if form is empty
    if not json:
        http_raise_unprocessable_entity(reason="Please fill at least one field.")

    await clear_user_cache(user=candidate, r_client=r_client)
    # update model
    query = (
        update(User)
        .where(User.uid == candidate.uid)
        .values(**json)
    )
    await db.execute(query)
    await db.commit()
    
    logger.info(f"successfully updated data for user: {candidate.uid}")

    candidate = await db.get(User, candidate.uid)
    await set_user_cache(user=candidate, r_client=r_client)
    return candidate


async def add_users_to_admin_group(
    id: str, user: User, db: AsyncSession, r_client: redis.Redis
) -> MessageResponse:
    """
    Adds multiple `User`s to `admin` group.

    Args:
        id: Comma seperated string list of `id`s for querying `User`s to be added to `admin` group
        user: Logged in `User` instance
        db: Asynchronous database connection instance

    Raises:
        HTTPException:
            403: One of the queried `User`s to be added to `admin` group is a superuser
            404: Not a single `User` found

    """
    affected_rows = 0
    uid_list = await validate_uid_list(uid_list=id, model_name="user")

    query = select(User).where(User.uid.in_(uid_list)).where(User.uid != user.uid)
    executed_query = await db.execute(query)
    candidates = executed_query.unique().scalars().all()
    if not candidates:
        http_raise_not_found(reason="No valid user found to add to admin group.")

    for candidate in candidates:
        # raise error if any  user is in superuser group
        if candidate.role == UserRoleChoices.SUPERUSER:
            http_raise_forbidden(reason="Failed to add Superuser to admin group.")
        # add user to admin group if user is not in admin group alreafy
        if candidate.role != UserRoleChoices.ADMIN:
            candidate.role = UserRoleChoices.ADMIN
            db.add(candidate)
            await clear_user_cache(user=candidate, r_client=r_client)
            affected_rows += 1

    await db.commit()
    return {"message": f"Successfully added {affected_rows} users to admin group."}


async def add_users_to_user_group(
    id: str, user: User, db: AsyncSession, r_client: redis.Redis
) -> MessageResponse:
    """
    Adds multiple `User`s to `user` group.

    Args:
        id: Comma seperated string list of `id`s for querying `User`s to be addeed to `user` group
        user: Logged in `User` instance
        db: Asynchronous database connection instance

    Raises:
        HTTPException:
            403: One of the queried `User`s to be added to `user` group is a superuser
            404: Not a single `User` found

    """
    affected_rows = 0
    uid_list = await validate_uid_list(uid_list=id, model_name="user")

    query = select(User).where(User.uid.in_(uid_list)).where(User.uid != user.uid)
    executed_query = await db.execute(query)
    candidates = executed_query.unique().scalars().all()
    if not candidates:
        http_raise_not_found(reason="No valid user found to add to user group.")

    for candidate in candidates:
        # raise error if any user is in superuser group
        if candidate.role == UserRoleChoices.SUPERUSER:
            http_raise_forbidden(reason="Failed to add Superuser to user group.")
        # add user to admin group if user is not in normal user group and superuser group already
        if candidate.role != UserRoleChoices.USER:
            candidate.role = UserRoleChoices.USER
            await clear_user_cache(user=candidate, r_client=r_client)
            affected_rows += 1

    await db.commit()
    return {"message": f"Successfully removed {affected_rows} users to user group."}


async def add_user_to_superuser_group(
    user: User, candidate_uid: UUID, password: str, db: AsyncSession, r_client: redis.Redis
) -> MessageResponse:
    """
    Args:
        user: Logged in `User` instance
        canididate_uid: UUID for candidate `User` to be added to `superuser` group
        password: String value used to authorize action (expected to match logged in `User`'s password)
        db: Asynchronous database connection instance

    Raises:
        HTTPException:
            403:
                -Logged in `User` has no password set
                -Entered `password` does not match logged in `User`'s password
            404: Candidate `User` does not exist
            422:
                -Logged in `User` is attempting to perform action on self
                -Candidate `User` is already a superuser
    """
    candidate = await get_user_by_uid(id=candidate_uid, db=db, r_client=r_client)
    # raise error if candidate is logged in user.
    if candidate == user:
        http_raise_unprocessable_entity(
            reason="User cannot assign self to superuser role."
        )
    # raise error if candidate is already a superuser
    if candidate.role == UserRoleChoices.SUPERUSER:
        http_raise_unprocessable_entity(reason="This user is already a superuser.")

    if not user.password:
        http_raise_forbidden(
            reason="User password not set. Set password with email through account recovery process."
        )
    # raise error if superuser provided wrong password to perform action
    superuser_password_correct = check_password(
        password=password, hashed_password=user.password
    )
    if not superuser_password_correct:
        http_raise_forbidden(reason="Superuser password is incorrect.")

    await clear_user_cache(user=candidate, r_client=r_client)
    query = (
        update(User)
        .where(User.uid == candidate.uid)
        .values(role=UserRoleChoices.SUPERUSER, is_hidden=True)
    )
    await db.execute(query)
    await db.commit()
    
    return {"message": "Successfully added 1 user to superuser group."}


async def delete_user(id: UUID, db: AsyncSession, r_client: redis.Redis) -> MessageResponse:
    """
    Deletes multiple `User`s from database.

    Args:
        id: UUID for `User` to be deleted
        db: Asynchronous database connection instance

    Raises:
        HTTPException 404: `User` does not exist
    """
    user = await get_user_by_uid(id=id, db=db, r_client=r_client)
    await clear_user_cache(user=user, r_client=r_client)
    
    query = delete(User).where(User.uid == user.uid)
    await db.execute(query)
    await db.commit()

    return {"message": "successfully deleted user."}


async def mass_delete_users(id: str, user: User, db: AsyncSession, r_client: redis.Redis) -> MessageResponse:
    """
    Deletes multiple `User`s from database.

    Args:
        id: Comma seperated string list of `id`s for querying `User`s to be deleted
        user: Logged in `User`
        db: Asynchronous database connection instance

    Raises:
        HTTPException 404: Not a single `User` found
    """
    id_list = await validate_uid_list(uid_list=id, model_name="user")
    affected_rows = 0
    query = select(User).where(User.uid.in_(id_list)).where(User.uid != user.uid)
    executed_query = await db.execute(query)
    user_list = executed_query.unique().scalars().all()
    if not user_list:
        http_raise_not_found(reason="No matching blacklisted user was found to delete.")

    for candidate in user_list:
        # raise error if any of the candidates to be mass deleted is a superuser
        if candidate.role == UserRoleChoices.SUPERUSER:
            http_raise_forbidden(reason="Failed to delete superuser account.")

        # add user email to blacklist
        email_is_blacklisted = await check_email_in_blacklist(
            email=candidate.email, db=db
        )
        if not email_is_blacklisted:
            await add_email_to_blacklist(email=candidate.email, db=db)

        # delete user account
        await db.delete(candidate)
        await clear_user_cache(user=candidate, r_client=r_client)
        affected_rows += 1

    await db.commit()
    return {"message": f"Successully deleted {affected_rows} users."}


async def mass_restrict_users(id: str, user: User, db: AsyncSession, r_client: redis.Redis) -> MessageResponse:
    """
    Restricts multiple `User`s,
    disabling affected `User`s accounts from being accessible from actions such as login, token refresh

    Args:
        id: Comma seperated string list of `id`s for querying `User`s to be restricted.
        user: Logged in `User` instance
        db: Asynchronous  database connection instance

    Raises:
        HTTPException:
            403: One of the queried `User`s is a superuser
            404: Not a single `User` found
    """
    id_list = await validate_uid_list(uid_list=id, model_name="user")
    affected_rows = 0
    query = select(User).where(User.uid.in_(id_list)).where(User.uid != user.uid)
    executed_query = await db.execute(query)
    user_list = executed_query.unique().scalars().all()
    if not user_list:
        http_raise_not_found(
            reason="No matching blacklisted user was found to unrestrict."
        )

    for candidate in user_list:
        if candidate.role == UserRole.SUPERUSER:
            http_raise_forbidden(reason="Failed to restrict superuser account.")
        if candidate.active:
            candidate.active = False
            db.add(candidate)
            await clear_user_cache(user=candidate, r_client=r_client)
            affected_rows += 1

    await db.commit()
    return {"message": f"Successfully restricted {affected_rows} users."}


async def mass_unrestrict_users(
    id: str, user: User, db: AsyncSession, r_client: redis.Redis
) -> MessageResponse:
    """
    Unrestricts multiple `User`s, enabling affected `User`s accounts to become accessible.

    Args:
        id: Comma seperated string list of `id`s for querying `User`s to be restricted.
        user: Logged in `User` instance
        db: Asynchronous  database connection instance

    Raises:
        HTTPException:
            403: One of the queried `User`s is a superuser
            404: Not a single `User` found
    """
    id_list = await validate_uid_list(uid_list=id, model_name="user")
    affected_rows = 0
    query = select(User).where(User.uid.in_(id_list)).where(User.uid != user.uid)
    executed_query = await db.execute(query)
    user_list = executed_query.unique().scalars().all()
    if not user_list:
        http_raise_not_found(
            reason="No matching blacklisted user was found to ununrestrict."
        )

    for candidate in user_list:
        if candidate.role == UserRole.SUPERUSER:
            http_raise_forbidden(reason="Failed to unrestrict superuser account.")
        if not candidate.active:
            candidate.active = True
            db.add(candidate)
            await clear_user_cache(user=candidate, r_client=r_client)
            affected_rows += 1

    await db.commit()
    return {"message": f"Successfully unrestricted {affected_rows} users."}
