from datetime import datetime, timezone
from enum import Enum
from typing import Any, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.generics.validator_schemas import PasswordValidator
from src.apps.chat.schemas.chat_validators import ChatroomValidator
from src.db.models import Chatroom, User
from src.apps.user.schemas.base_schemas import UserBasic


class ChatroomType(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    PERSONAL = "personal"


class ChatroomUserStatus(str, Enum):
    MEMBER = "member"
    MODERATOR = "moderator"
    CREATOR = "creator"
    SUCCESSOR = "successor"
    REMOVED = "removed"


class ChatroomMemberRole(str, Enum):
    ALL = "all"
    MODERATOR = "moderator"
    CREATOR = "creator"
    REMOVED = "removed"


class ChatroomPrivatePublicType(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    ALL = "all"


class MessageType(str, Enum):
    USER = "user"
    ANNOUNCEMENT = "announcement"
    INFO = "info"
    ALERT = "alert"


class ChatroomsSort(str, Enum):
    NAME = "name"
    DATE = "date"
    POPULARITY = "popularity"
    ACTIVITY = "activity"


class MessageContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"


class RawChatroomList(BaseModel):
    chatrooms: List[Chatroom]


class ChatroomCreateForm(PasswordValidator):
    name: str
    about: str = Field(max_length=255, min_length=25)
    room_type: ChatroomPrivatePublicType
    password: str | None = None
    confirm_password: str | None = None

    @model_validator(mode="after")
    def modify_fields_after(self):
        if (self.room_type != ChatroomType.PRIVATE) and (self.password):
            raise ValueError(
                "Please clear password. Only a private chatroom can be password protected."
            )
        if (self.room_type == ChatroomType.PRIVATE) and (not self.password):
            raise ValueError("No password was provided for private chatroom.")
        return self


class AdminChatroomCreateForm(ChatroomCreateForm):
    original_creator_username: str

    @model_validator(mode="after")
    def username_to_lowercase(self):
        self.original_creator_username = self.original_creator_username.lower()

        return self


class ChatroomUser(UserBasic):
    user_status: ChatroomUserStatus | None = ChatroomUserStatus.REMOVED


class ChatroomUpdate(ChatroomValidator, PasswordValidator):
    name: str | None = None
    about: str | None = None
    password: str | None = None
    confirm_password: str | None = None


class ChatroomDetails(BaseModel):
    uid: UUID
    name: str
    about: str
    room_type: str
    members_count: int
    created_at: datetime
    modified_at: datetime
    original_creator_username: str

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    def modify_fields_before(cls, data: Any):
        if isinstance(data, dict):
            if ("created_at" in data) and (str(data["created_at"]).isnumeric()):
                parsed_date = datetime.fromtimestamp(
                    float(data["created_at"]), tz=timezone.utc
                ).date()
                data["created_at"] = parsed_date
            if ("modified_at" in data) and (str(data["modified_at"]).isnumeric()):
                parsed_date = datetime.fromtimestamp(
                    float(data["modified_at"]), tz=timezone.utc
                ).date()
                data["modified_at"] = parsed_date
        return data


class ChatroomDetailsList(BaseModel):
    chatrooms: List[ChatroomDetails] | None = []


class ChatroomDetailsExtended(ChatroomDetails):
    user_status: ChatroomUserStatus | None = ChatroomUserStatus.REMOVED
    secret_mode: bool | None = None
    user_is_hidden: bool | None = False
    active_visitors: int | None = 0


class ChatroomDetailsExtendedList(BaseModel):
    chatrooms: List[ChatroomDetailsExtended] | None = []


class MessageCreate(BaseModel):
    type: MessageType
    content: str
    content_type: str
    id: UUID
    sender_uid: UUID | None = None


class MessageReadCreate(BaseModel):
    id: int | None = None
    type: str
    content: str
    content_type: MessageContentType
    sender_username: str | None = None
    sender_uid: UUID | None = None
    created_at: datetime | None = None
    recorded: bool | None = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    def modify_fields_before(cls, data: Any):
        if isinstance(data, dict):
            if ("created_at" in data) and (str(data["created_at"]).isnumeric()):
                parsed_date = datetime.fromtimestamp(
                    float(data["created_at"]), tz=timezone.utc
                ).date()
                data["created_at"] = parsed_date
        return data


class MessagesList(BaseModel):
    room_type: str
    messages: List[MessageReadCreate]


class AnonUserID(BaseModel):
    anonymous_user_uid: UUID
