import os

from slowapi import Limiter
from slowapi.util import get_remote_address

active_environment_is_testing = os.getenv("TESTING")

LIMITER_TOGGLE = False if active_environment_is_testing else True
# LIMITER_TOGGLE = False

api_limiter = Limiter(key_func=get_remote_address, enabled=LIMITER_TOGGLE)
