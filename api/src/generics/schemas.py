from enum import Enum

from pydantic import BaseModel


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class OptionalBooleanString(str, Enum):
    ALL = "all"
    TRUE = "true"
    FALSE = "false"


class SortByDateOrID(str, Enum):
    DATE = "date"
    ID = "id"


class ConfirmationText(BaseModel):
    text: str


class MessageResponse(BaseModel):
    message: str


class IsValidResponse(BaseModel):
    valid: bool
