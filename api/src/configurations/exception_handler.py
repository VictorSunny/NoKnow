from logging import getLogger
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError
from sqlalchemy.dialects.postgresql import asyncpg
from pydantic_core import ValidationError as PydanticValidationError

from redis.exceptions import ConnectionError as RedisConnectionErrors

from src.exceptions.http_exceptions import (
    http_raise_bad_request,
    http_raise_internal_server_error,
    http_raise_service_unavailable,
)


logger = getLogger(__name__)


def register_app_exceptions(app):

    @app.exception_handler(HTTPException)
    async def handle_http_exception_class(request: Request, exc: HTTPException):
        logger.error(exc.detail)
        error_response = JSONResponse(
            status_code=exc.status_code,
            content={
                "status": exc.status_code,
                "detail": exc.detail,
                "path": str(request.url.path),
            },
        )
        return error_response

    @app.exception_handler(RedisConnectionErrors)
    async def handle_redis_connection_error(
        request: Request, exc: RedisConnectionErrors
    ):
        logger.error("redis connection error", exc)
        print(exc)
        http_raise_service_unavailable("Unable to send otp right now. Try again later.")

    @app.exception_handler(PydanticValidationError)
    async def pydantic_validation_error(request: Request, exc: PydanticValidationError):
        logger.error(exc)
        http_raise_service_unavailable("Server-side error processing data.")

    @app.exception_handler(DBAPIError)
    async def handle_db_api_error(request: Request, exc: DBAPIError):
        error = exc.orig
        error_dialects = asyncpg.AsyncAdapt_asyncpg_dbapi
        logger.debug(exc)

        if isinstance(error, error_dialects.IntegrityError):
            http_raise_bad_request(reason="Data error.")
        if isinstance(error, error_dialects.InterfaceError):
            http_raise_service_unavailable(
                reason="Database service is currently unavailable. Try again later."
            )
        if isinstance(error, error_dialects.ProgrammingError):
            http_raise_service_unavailable(reason="Database error. Try again later.")
        if isinstance(error, error_dialects.Error):
            http_raise_bad_request(reason="Invalid data. Confirm and try again.")

        http_raise_service_unavailable(reason="Unexpected database error.")

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception):
        logger.debug(exc)
        error_response = JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "detail": {
                    "error": "unexpected_server_error",
                    "message": "An unexpected server error occured. This is not your fault."
                },
                "path": str(request.url.path),
            },
        )
        return error_response