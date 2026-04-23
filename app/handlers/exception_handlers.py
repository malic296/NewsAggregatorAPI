from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from app.core.errors import AppError
from fastapi import Request, status, HTTPException
from app.schemas.responses import BaseResponse
import logging

logger = logging.getLogger(__name__)

def create_error_response(err: AppError) -> JSONResponse:
    response: BaseResponse = BaseResponse(
        success=False,
        message=err.public_message
    )

    return JSONResponse(
        status_code=err.status_code,
        content=response.model_dump()
    )

async def unexpected_exception_handler(request: Request, err: Exception):
    logger.error(f"Unexpected Error: {str(err)} | Path: {request.url.path}", extra={"exception": err})
    return create_error_response(
        AppError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            public_message=f"Server failed unexpectedly. Try again in a moment."
        )
    )

async def internal_exception_handler(request: Request, err: AppError):
    if err.internal_message:
        logger.error(err.internal_message, extra={"exception": err})

    return create_error_response(err=err)


async def http_exception_handler(request: Request, err: HTTPException):
    status_code = getattr(err, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR)

    if status_code >= 500:
        logger.error(
            f"Server Error {status_code} | Path: {request.url.path} | Error: {str(err)}",
            exc_info=True
        )
        return create_error_response(
            AppError(
                status_code=500,
                public_message="Internal Server Error."
            )
        )

    if isinstance(err, RequestValidationError):
        return create_error_response(
            AppError(
                status_code=422,
                public_message="Validation failed.",
            )
        )

    msg = getattr(err, "detail", "An error occurred.")
    return create_error_response(
        AppError(status_code=status_code, public_message=msg)
    )
