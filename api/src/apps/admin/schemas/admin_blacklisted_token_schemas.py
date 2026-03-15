from enum import Enum


class TokenValidity(str, Enum):
    ALL = "all"
    FRESH = "fresh"
    EXPIRED = "expired"
