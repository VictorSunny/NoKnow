from pydantic import BaseModel, field_validator, model_validator

from src.utilities.utilities import check_password_strength


class PasswordValidator(BaseModel):

    @field_validator("password", mode="after", check_fields=False)
    @classmethod
    def check_password_strength(cls, v):
        if type(v) == str:
            test_result = check_password_strength(password=v)
            password_strong = test_result["strong"]
            if password_strong is False:
                error_message = test_result["message"]
                raise ValueError(error_message)
        return v

    @model_validator(mode="after")
    def check_passwords_match(self):
        if ("password" in self.__class__.model_fields) and (
            "confirm_password" in self.__class__.model_fields
        ):
            if self.password and not self.confirm_password:
                raise ValueError("No confirmation password was provided.")
            if self.password != self.confirm_password:
                raise ValueError("Passwords do not match.")
        return self
