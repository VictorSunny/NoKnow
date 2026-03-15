from pydantic import BaseModel, field_validator


class ChatroomValidator(BaseModel):
    @field_validator("about", mode="before", check_fields=False)
    @classmethod
    def parse_about(cls, v):
        min_about_length = 25
        if (v is not None) and (len(v) < min_about_length):
            raise ValueError(
                f"Chatroom description is too short. must be at least {min_about_length} characters long."
            )
        return v
