from enum import Enum

from pydantic import BaseModel

from src.db.models import BlacklistedEmail, BlacklistedToken


class FromDate(str, Enum):
    ALL = "all"
    ONE_DAY = "1d"
    ONE_WEEK = "7d"
    ONE_MONTH = "1m"
    THREE_MONTHS = "3m"
    SIX_MONTHS = "6m"
    ONE_YEAR = "1y"


class RawBlacklistedTokenList(BaseModel):
    tokens: BlacklistedToken


class RawBlacklistedEmailList(BaseModel):
    tokens: BlacklistedEmail
