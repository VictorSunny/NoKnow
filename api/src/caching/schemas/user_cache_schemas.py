from typing import Any
from uuid import UUID
from pydantic import BaseModel, model_validator

from src.utilities.utilities import is_bool, is_float, is_uuid, str_to_bool


class UserCache(BaseModel):
    uid: UUID | str

    first_name: str
    last_name: str
    username: str
    email: str
    bio: str
    password: str
    role: str
    google_oauth2_id: str | None = None

    created_at: str | float
    modified_at: str | float
    last_seen: str | float

    active: str | bool
    is_hidden: str | bool
    is_two_factor_authenticated: str | bool

    @model_validator(mode="before")
    def validate_values(cls, data: Any):
        if isinstance(data, dict):
            uid_is_valid = is_uuid(uuid_str=data.get("uid"))
            created_at_is_valid = is_float(variable=data.get("created_at"))
            modified_at_is_valid = is_float(variable=data.get("modified_at"))

            active_is_valid = is_bool(variable=data.get("active"))
            is_hidden_is_valid = is_bool(variable=data.get("is_hidden"))
            is_two_factor_authenticated_is_valid = is_bool(
                variable=data.get("is_two_factor_authenticated")
            )

            if not uid_is_valid:
                raise Exception("user cache uid value is not a valid uid.")
            if not created_at_is_valid:
                raise Exception("user cache created_at value is not a valid float.")
            if not modified_at_is_valid:
                raise Exception("user cache modified_at value is not a valid float.")
            if not active_is_valid:
                raise Exception("user cache active value is not a valid boolean")
            if not is_hidden_is_valid:
                raise Exception("user cache is_hidden value is not a valid boolean")
            if not is_two_factor_authenticated_is_valid:
                raise Exception(
                    "user cache is_two_factor_authenticated value is not a valid boolean"
                )
        return data

    @model_validator(mode="after")
    def modify_fields(self):
        self.uid = UUID(self.uid)
        self.created_at = float(self.created_at)
        self.modified_at = float(self.modified_at)

        self.active = str_to_bool(self.active)
        self.is_hidden = str_to_bool(variable=self.is_hidden)
        self.is_two_factor_authenticated = str_to_bool(
            variable=self.is_two_factor_authenticated
        )

        return self
