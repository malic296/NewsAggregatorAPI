from app.core.errors import RateLimitExceededError
from fastapi import Request
import logging
from app.handlers.exception_handlers import create_error_response
from app.core.errors import AppError
from fastapi import status

logger = logging.getLogger(__name__)

async def rate_limit_middleware(request: Request, call_next):
    try:
        authorization_header = request.headers.get("Authorization")
        client_key = authorization_header.removeprefix("Bearer").strip() if authorization_header else (request.client.host if request.client else "unknown")
        if not request.app.state.services.cache_service.can_request_go_through(client_key):
            return create_error_response(RateLimitExceededError())
    except Exception as e:
        return create_error_response(
            AppError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                public_message=f"Server failed unexpectedly. Try again in a moment."
            )
        )

    response = await call_next(request)
    return response

async def logging_middleware(request: Request, call_next):
    response = await call_next(request)
    try:
        logger.info(f"IP: {request.client.host if request.client else 'Unknown'} | {request.method} {request.url.path} | Status: {response.status_code}")
    except Exception as e:
        print(f"[ CRITICAL] Logging failed because: {e}")

    return response