from datetime import datetime, timezone
from enum import Enum
from typing import Any, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from src.db.models import User
from src.configurations.apps_config.config import Config
from src.utilities.utilities import check_fresh


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERUSER = "superuser"


class UserRoleChoices(str, Enum):
    ALL = "all"
    USER = "user"
    ADMIN = "admin"
    SUPERUSER = "superuser"


class UserAdminUserRoleChoices(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserFrienshipStatus(str, Enum):
    FRIENDED = "friended"
    UNDFRIENDED = "unfriended"
    REQUESTED = "requested"
    PENDING = "pending"


class UserSortBy(str, Enum):
    USERNAME = "username"
    DATE = "date"


class AdminUserSortBy(str, Enum):
    USERNAME = "username"
    NAME = "name"
    DATE = "date"


class UserBase(BaseModel):
    first_name: str
    last_name: str
    username: str
    bio: str | None = None


class RawUserList(BaseModel):
    users: List[User]


class UserBasic(UserBase):
    uid: UUID
    created_at: datetime = Field(alias="joined")
    last_seen: datetime
    online: bool | None = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    # transform "created_at" timestamp to datetime for presentation
    @model_validator(mode="before")
    def modify_fields(cls, data: Any):
        if isinstance(data, dict):
            if "username" in data:
                if not str(data["username"]).isalnum():
                    raise ValueError("username can contain only letters and numbers")
                data["username"] = str(data["username"]).lower()
            if ("created_at" in data) and (type(data["created_at"] != datetime)):
                parsed_date = datetime.fromtimestamp(
                    data["created_at"], tz=timezone.utc
                )
            if ("last_seen" in data) and (type(data["last_seen"] != datetime)):
                parsed_date = datetime.fromtimestamp(data["last_seen"], tz=timezone.utc)
                data["last_seen"] = parsed_date
        return data

    @model_validator(mode="after")
    def modify_online_status(self):
        if self.last_seen:
            self.online = check_fresh(
                exp=(60 * Config.ACCESS_TOKEN_EXPIRY_MINUTES), created_at=self.last_seen
            )
        return self


class AdminUserBasic(UserBasic):
    role: UserRole


class UserPrivate(UserBasic):
    email: EmailStr
    is_hidden: bool
    is_two_factor_authenticated: bool


class UserList(BaseModel):
    users: List[UserBasic]
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdminUserList(BaseModel):
    users: List[AdminUserBasic]
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UserPrivateList(BaseModel):
    users: List[UserPrivate]


class UserComplete(UserPrivate):
    role: UserRoleChoices
    active: bool


class FriendshipStatus(BaseModel):
    friendship_status: UserFrienshipStatus
