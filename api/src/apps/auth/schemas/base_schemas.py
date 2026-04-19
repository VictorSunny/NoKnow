from datetime import datetime, timezone
from enum import Enum
from typing import Any, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, model_validator

from src.apps.user.schemas.base_schemas import UserAdminUserRoleChoices
from src.utilities.utilities import check_expired
from src.generics.validation_schemas import PasswordValidator
from src.apps.auth.schemas.auth_validators import UserValidator


class OTPType(str, Enum):
    SIGNUP = "signup"
    LOGIN = "login"
    EMAIL_CHANGE = "email_change"
    PASSWORD_CHANGE = "password_change"

    def __str__(self):
        return str(self.value)


class TokenUse(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    OTP = "otp"


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserTwoFactorAuthStatus(BaseModel):
    is_two_factor_authenticated: bool
    model_config = ConfigDict(populate_by_name=True)


class EmailForm(BaseModel):
    email: EmailStr


class UserHiddenStatus(BaseModel):
    is_hidden: bool


class OTPForm(BaseModel):
    email: EmailStr
    otp: int


class OTPJWTResponse(BaseModel):
    otp_jwt: str


class JWTUnencodedDict(BaseModel):
    sub: str


class PasswordForm(BaseModel):
    password: str


class LoginForm(BaseModel):
    email: EmailStr
    password: str


class EmailUsernameForm(BaseModel):
    email: EmailStr
    username: str


class UserBase(BaseModel):
    first_name: str
    last_name: str
    username: str
    bio: str | None = None


class UserPasswordEmail(UserBase):
    email: EmailStr
    password: str
    google_oauth2_id: str | None = None


class UserBasicUpdate(UserValidator):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    bio: str | None = None
    is_hidden: bool | None = None

    @model_validator(mode="after")
    def modify_fields(self):
        if self.first_name:
            self.first_name = self.first_name.title()
        if self.last_name:
            self.last_name = self.last_name.title()
        if self.username:
            self.username = self.username.lower()

        return self


class UserPasswordUpdate(PasswordValidator):
    old_password: str | None = None
    password: str
    confirm_password: str


class UserEmailPasswordForm(EmailForm, PasswordForm):
    pass


class UserCreate(UserPasswordEmail, UserValidator, PasswordValidator):
    confirm_password: str

    @model_validator(mode="after")
    def modify_fields(self):

        # transform name values to title case
        # transform email and username values to lower case
        self.first_name = self.first_name.title()
        self.last_name = self.last_name.title()
        self.email = self.email.lower()
        self.username = self.username.lower()

        return self


class UserCreateComplete(UserCreate):
    role: UserAdminUserRoleChoices


class UserUpdateComplete(UserBasicUpdate, PasswordValidator):
    active: bool | None = None
    email: str | None = None
    password: str | None = None
    confirm_password: str | None = None
    role: UserAdminUserRoleChoices | None = None


class BlacklistedTokenRead(BaseModel):
    id: int
    jti: UUID
    exp: datetime
    created_at: datetime
    expired: bool | None = None

    @model_validator(mode="before")
    def modify_fields(cls, data: Any):
        if isinstance(data, dict):
            if ("created_at" in data) and (str(data["created_at"]).isnumeric()):
                parsed_date = datetime.fromtimestamp(
                    float(data["created_at"]), tz=timezone.utc
                )
                data["created_at"] = parsed_date
            if ("exp" in data) and (str(data["exp"]).isnumeric()):
                parsed_date = datetime.fromtimestamp(
                    float(data["exp"]), tz=timezone.utc
                )
                data["exp"] = parsed_date
        return data

    @model_validator(mode="after")
    def check_expired(self):
        if self.exp:
            self.expired = check_expired(self.exp)
        return self


class BlacklistedTokenList(BaseModel):
    tokens: List[BlacklistedTokenRead]


class BlacklistedEmailCreate(BaseModel):
    sub: EmailStr


class BlacklistedEmailRead(BaseModel):
    sub: EmailStr
    id: int
    created_at: datetime

    @model_validator(mode="before")
    def modify_fields(cls, data: Any):
        if isinstance(data, dict):
            if ("created_at" in data) and (str(data["created_at"]).isnumeric()):
                parsed_date = datetime.fromtimestamp(
                    float(data["created_at"]), tz=timezone.utc
                )
                data["created_at"] = parsed_date
        return data


class BlacklistedEmailList(BaseModel):
    emails: List[BlacklistedEmailRead]


class GoogleLoginForm(BaseModel):
    id: int
