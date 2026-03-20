from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.apps.auth.services.base_services import user_create
from src.apps.user.schemas.base_schemas import (
    AdminUserList,
    AdminUserSortBy,
    UserComplete,
    UserList,
    UserRoleChoices,
)
from src.apps.admin.schemas.admin_base_schemas import FromDate
from src.apps.admin.services.admin_user_services import (
    add_user_to_superuser_group,
    add_users_to_admin_group,
    add_users_to_user_group,
    delete_user,
    get_all_created_users,
    mass_delete_users,
    mass_restrict_users,
    mass_unrestrict_users,
    update_user_full_data,
)
from src.apps.user.services.base_services import get_user_by_uid
from src.apps.auth.schemas.base_schemas import (
    PasswordForm,
    UserCreateComplete,
    UserUpdateComplete,
)
from src.apps.admin.services.admin_auth_services import (
    get_current_admin_user,
    get_current_superuser,
)
from src.db.database import get_session
from src.db.models import User
from src.generics.schemas import MessageResponse, OptionalBooleanString, SortOrder


admin_user_router = APIRouter()


@admin_user_router.get("", status_code=status.HTTP_200_OK)
async def get_admin_user(
    id: UUID | None = None,
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_session),
) -> UserComplete:
    """
    Get user details.
    """
    if id:
        user = await get_user_by_uid(id=id, db=db)
    return user


@admin_user_router.post("", status_code=status.HTTP_201_CREATED)
async def create_admin_user(
    json: UserCreateComplete,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_superuser),
) -> UserComplete:
    """
    Create a new admin or normal user.
    """
    response = await user_create(json=json, role=json.role, no_email_auth=True, db=db)
    return response


@admin_user_router.patch("", status_code=status.HTTP_200_OK)
async def update_user_data(
    json: UserUpdateComplete,
    id: UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_admin_user),
) -> UserComplete:
    """
    Update user data.
    """
    response = await update_user_full_data(id=id, json=json, user=user, db=db)
    return response


@admin_user_router.delete("", status_code=status.HTTP_200_OK)
async def delete_user_from_db(
    id: UUID | None = None,
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_session),
) -> UserComplete:
    """
    Delete/Suspend user account.
    """
    if id:
        user = await delete_user(id=id, db=db)
    return user


@admin_user_router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_users(
    sort: AdminUserSortBy | None = AdminUserSortBy.USERNAME,
    order: SortOrder | None = SortOrder.ASC,
    role: UserRoleChoices | None = UserRoleChoices.ALL,
    active: OptionalBooleanString | None = OptionalBooleanString.ALL,
    google_signup: OptionalBooleanString | None = OptionalBooleanString.ALL,
    page: int | None = 1,
    from_date: FromDate | None = FromDate.ALL,
    search_query: str | None = None,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_admin_user),
) -> AdminUserList:
    """
    Get paginated users.
    """
    response = await get_all_created_users(
        sort=sort,
        role=role,
        order=order,
        active=active,
        google_signup=google_signup,
        page=page,
        search_query=search_query,
        from_date=from_date,
        user=user,
        db=db,
    )
    return response


@admin_user_router.delete("/all", status_code=status.HTTP_200_OK)
async def delete_marked_users(
    id: str,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_superuser),
) -> MessageResponse:
    """
    Delete multiple users.
    """
    response = await mass_delete_users(id=id, user=user, db=db)
    return response


@admin_user_router.patch("/all/restrict", status_code=status.HTTP_200_OK)
async def patch_mass_restrict_users(
    id: str,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_superuser),
) -> MessageResponse:
    """
    Restrict multiple user accounts.
    """
    response = await mass_restrict_users(id=id, db=db, user=user)
    return response


@admin_user_router.patch("/all/unrestrict")
async def patch_mass_unrestrict_users(
    id: str,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_superuser),
) -> MessageResponse:
    """
    Unrestrict multiple user accounts.
    """
    response = await mass_unrestrict_users(id=id, db=db, user=user)
    return response


@admin_user_router.patch("/groups/admin/add", status_code=status.HTTP_200_OK)
async def patch_add_users_to_admin_group(
    id: str,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_superuser),
) -> MessageResponse:
    """
    Add multiple users to admin-user group.
    """
    response = await add_users_to_admin_group(id=id, user=user, db=db)
    return response


@admin_user_router.patch("/groups/user/add", status_code=status.HTTP_200_OK)
async def patch_add_users_to_user_group(
    id: str,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_superuser),
) -> MessageResponse:
    """
    Add multiple users to normal-user group.
    """
    response = await add_users_to_user_group(
        id=id,
        user=user,
        db=db,
    )
    return response


@admin_user_router.post(
    "/groups/superuser/add",
    status_code=status.HTTP_200_OK,
)
async def assign_superuser_role_to_user(
    id: UUID,
    password_form: PasswordForm,
    user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_session),
) -> MessageResponse:
    """
    Add user to superuser group.
    """
    response = await add_user_to_superuser_group(
        user=user, password=password_form.password, candidate_uid=id, db=db
    )
    return response
