import ast
import json
from asyncio import get_running_loop
from datetime import datetime, timedelta, timezone
import re
from typing import Any, List
from urllib.parse import unquote
from uuid import UUID

from bcrypt import checkpw, gensalt, hashpw

from src.exceptions.http_exceptions import http_raise_unprocessable_entity


def hash_password(password: str) -> str:
    encoded_pw = password.encode("utf-8")
    salt = gensalt()
    hash = hashpw(encoded_pw, salt)
    decoded_hash = hash.decode("utf-8")
    return decoded_hash


def check_password(password: str, hashed_password: str) -> bool:
    encoded_pw = password.encode("utf-8")
    hashed_pw = hashed_password.encode("utf-8")
    is_valid = checkpw(encoded_pw, hashed_pw)

    return is_valid


def extract_token(token_dict: dict, key: str):
    data = json.loads(token_dict.body)
    token = data[key]

    return token


def timestamp_now(exp: int | None = 0) -> float:
    """
    get the current utc timestamp.
    accepts `exp`(seconds) arg get time with offset.
    """
    current_time = datetime.now() + timedelta(seconds=exp)
    time = current_time.astimezone(timezone.utc).timestamp()
    return time


def utc_time_now(exp: int | None = 0) -> datetime:
    current_time = datetime.now() + timedelta(seconds=exp)
    time = current_time.astimezone(timezone.utc)
    return time


def check_fresh(created_at: float, exp: int):
    """
    checks if an item is expired from it's time of creation - `created_at_timestamp`(utc timestamp),
    in relation to the provided expiry time - `exp`(seconds).
    Returns `True` if fresh, `False` if expired
    """
    # check if created at is datetime or float object
    # raise error if it is neither
    # convert to datetime if float
    if (type(created_at) != datetime) and (type(created_at) != float):
        raise ValueError("exp must be of datetime or float type.")
    if type(created_at) == float:
        created_at = datetime.fromtimestamp(exp)

    # check if created_at is less than the current time minus the expiry
    if created_at < (utc_time_now() - timedelta(seconds=exp)):
        return False
    return True


def check_expired(exp: datetime | float):
    if (type(exp) != datetime) and (type(exp) != float):
        raise ValueError("exp must be of datetime or float type.")
    if type(exp) == float:
        exp = datetime.fromtimestamp(exp)
    if exp > utc_time_now():
        return False
    return True


async def validate_uid_list(
    model_name: str, uid_list: str, safe: bool | None = False
) -> List[UUID]:
    """
    Takes string and returns list of valid `UUID`s.
    """

    parsed_uid_list = []
    uid_list = str(uid_list).strip().split(",")

    for list_item in uid_list:
        # list_item = str(list_item).strip()
        try:
            parsed_uid_list.append(UUID(list_item))
        except ValueError:
            continue

    # confirm list contains at least one item after parsing
    if (len(parsed_uid_list) < 1) and not safe:
        http_raise_unprocessable_entity(f"Please enter a valid {model_name} UID")

    return parsed_uid_list


async def validate_int_list(
    model_name: str, int_string: str, safe: bool | None = False
) -> List[int]:
    seperated_list = int_string.strip().split(",")
    parsed_list = []
    for number in seperated_list:
        if str(number).isnumeric():
            parsed_list.append(int(number))

    if len(parsed_list) < 1 and not safe:
        http_raise_unprocessable_entity(f"please enter a valid {model_name} ID")

    return parsed_list


def check_password_strength(password: str):
    strong = True
    message = "Password is strong."
    if not re.search(r"[^A-Za-z0-9]", password):
        strong = False
        message = "Password is weak. Please enter at least symbol."
    if not re.search(r"[0-9]", password):
        strong = False
        message = "Password is weak. Please enter at least one number."
    if not re.search(r"[a-z]", password):
        message = "Password is weak. Please enter at least one lowercase letter."
        strong = False
    if not re.search(r"[A-Z]", password):
        message = "Password is weak. Please enter at least one uppercase letter."
        strong = False
    if len(password) < 8:
        message = "Password is weak. must be at least 8 characters long."
        strong = False

    result = {"strong": strong, "message": message}
    return result


def slugify_strings(string_list: List[str]):
    slug = "-".join(string_list)
    return slug


def unslugify_string(slug: str):
    unslugified = slug.replace("_", " ").replace("-", " ")
    return unslugified


def is_uuid(uuid_str):
    try:
        UUID(uuid_str)
        return True
    except:
        return False


def is_float(variable: Any):
    try:
        float(variable)
        return True
    except:
        return False


def offset_by_page(page_num: int, limit: int):
    if page_num > 1:
        offset = (page_num - 1) * limit
    else:
        offset = 0
    return offset


def decode_uri_string_to_list(uri_string: str):
    decoded_uri_list = unquote(uri_string).split(" ")[:4]
    decoded_uri_list = [query.lower() for query in decoded_uri_list]
    return decoded_uri_list
