from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    HASHING_ALGORITHM: str

    ACCESS_TOKEN_EXPIRY_MINUTES: int
    REFRESH_TOKEN_EXPIRY_DAYS: int

    DEBUG: bool

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    GOOGLE_REDIRECT_URI: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    REDIS_URL: str

    MAIL_USERNAME: str
    MAIL_FROM: str
    MAIL_PASSWORD: str
    MAIL_SERVER: str

    # ERROR CODES
    ACCOUNT_SUSPENDED_ERROR_CODE: str
    NOT_ADMIN_ERROR: str

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


Config = Settings()

# set postgres host to localhost if
#   1. not in debug mode
#   2. postgres is running on a seperate container, not as a shared service. debug mode is to be set off.
HOST = Config.POSTGRES_HOST if not Config.DEBUG else "localhost"

DATABASE_URL = f"postgresql://{Config.POSTGRES_USER}:{Config.POSTGRES_PASSWORD}@{HOST}:{Config.POSTGRES_PORT}/{Config.POSTGRES_DB}"
ASYNC_DATABASE_URL = f"postgresql+asyncpg://{Config.POSTGRES_USER}:{Config.POSTGRES_PASSWORD}@{HOST}:{Config.POSTGRES_PORT}/{Config.POSTGRES_DB}"


result_backend = Config.REDIS_URL
broker_url = Config.REDIS_URL
broker_connection_retry_on_startup = True

task_serializer = "json"
accept_content = ["json"]
result_serializer = "json"

# task_acks_late=True
# worker_prefetch_multiplier=1
# task_default_rate_limit="8/min"
