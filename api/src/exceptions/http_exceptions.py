from fastapi import HTTPException, status


def http_raise_internal_server_error(
    reason: str | None = "An unexpected server error occured. This is not your fault.",
    error: str | None = "unexpected_server_error",
):
    exception = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error": error,
            "message": reason,
        },
    )
    raise exception


def http_raise_service_unavailable(
    reason: str | None = "Server is currently unable to process your request.",
    error: str | None = "service_unavailable",
):
    exception = HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "error": error,
            "message": reason,
        },
    )
    raise exception


def http_raise_unauthorized(
    reason: str | None = "Confirm you are authorized to access this resource.",
    error: str | None = "user_not_authorized",
):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error": error,
            "message": reason,
        },
    )
    raise exception


def http_raise_forbidden(
    reason: str | None = "User not allowed to access resource.",
    error: str | None = "permission_denied",
):
    exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "error": error,
            "message": reason,
        },
    )
    raise exception


def http_raise_bad_request(
    reason: str | None = "Request could not be processed.",
    error: str | None = "bad_request",
):
    exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "error": error,
            "message": reason,
        },
    )
    raise exception


def http_raise_not_found(
    reason: str | None = "Requested resource not found.",
    error: str | None = "not_found",
):
    exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error": error,
            "message": reason,
        },
    )
    raise exception


def http_raise_conflict(
    reason: str | None = "Request could not be processed.",
    error: str | None = "conflicting_data",
):
    exception = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "error": error,
            "message": reason,
        },
    )
    raise exception


def http_raise_unprocessable_entity(
    reason: str | None = "Data unacceptable.",
    error: str | None = "unproccessable_data",
):
    exception = HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={
            "error": error,
            "message": reason,
        },
    )
    raise exception
