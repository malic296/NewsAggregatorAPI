from starlette.responses import JSONResponse
from app.core.errors import AppError
from fastapi import Request, status
from app.schemas.responses import BaseResponse
import logging


def create_error_response(err: AppError) -> JSONResponse:
    response: BaseResponse = BaseResponse(
        success=False,
        message=err.public_message
    )

    return JSONResponse(
        status_code=err.status_code,
        content=response.model_dump()
    )

async def global_exception_handler(request: Request, err: Exception):
    if isinstance(err, AppError):
        if err.internal_message:
            logging.getLogger(__name__).error(err.internal_message, extra={"exception": err})

        return create_error_response(err=err)

    else:
        logging.getLogger(__name__).error(f"Unexpected Error: {str(err)} | Path: {request.url.path}", extra={"exception": err})
        return create_error_response(
            AppError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                public_message=f"Server failed unexpectedly. Try again in a moment."
            )
        )