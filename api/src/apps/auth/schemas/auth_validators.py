from pydantic import BaseModel, field_validator


class UserValidator(BaseModel):
    @field_validator("first_name", mode="before", check_fields=False)
    @classmethod
    def parse_first_name(cls, v):
        if (v is not None) and (len(v) < 2):
            raise ValueError("First name is too short.")
        if (v is not None) and (type(v) == str) and (not v.isalpha()):
            raise ValueError("First name can contain only letters.")
        return v

    @field_validator("last_name", mode="before", check_fields=False)
    @classmethod
    def parse_last_name(cls, v):
        if v is not None and len(v) < 2:
            raise ValueError("Last name is too short.")
        if (v is not None) and (type(v) == str) and (not v.isalpha()):
            raise ValueError("last name can contain only letters.")
        return v

    @field_validator("username", mode="before", check_fields=False)
    @classmethod
    def parse_username(cls, v):
        if (v is not None) and (len(v) < 2):
            raise ValueError("Username is too short.")
        if (v is not None) and (type(v) == str) and (not v.isalnum()):
            raise ValueError("Username can contain only letter and numbers.")
        return v

    @field_validator("bio", mode="before", check_fields=False)
    @classmethod
    def parse_bio(cls, v):
        min_bio_length = 25
        if (v is not None) and (len(v) < min_bio_length):
            raise ValueError(
                f"Bio is too short. Should be at least {min_bio_length} characters."
            )
        return v
