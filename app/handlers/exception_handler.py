from starlette.responses import JSONResponse
from app.core.errors import AppError
from app.handlers import LoggingHandler
from fastapi import Request, status
from app.schemas.responses import BaseResponse

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
    logger: LoggingHandler = request.app.state.services.logger

    if isinstance(err, AppError):
        if err.internal_message:
            logger.handle(err.internal_message)

        return create_error_response(err=err)

    else:
        logger.handle(f"Unexpected Error: {str(err)} | Path: {request.url.path}")
        return create_error_response(
            AppError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                public_message=f"Server failed unexpectedly. Try again in a moment."
            )
        )