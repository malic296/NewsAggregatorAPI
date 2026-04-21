from app.core.errors import RateLimitExceededError
from app.handlers.exception_handler import create_error_response
from fastapi import Request
import logging

async def rate_limit_middleware(request: Request, call_next):
    authorization_header = request.headers.get("Authorization")
    if authorization_header:
        client_key = authorization_header.removeprefix("Bearer").strip()
    else:
        client_key = request.client.host if request.client else "unknown"
    allowed = request.app.state.services.cache_service.can_request_go_through(client_key)
    if not allowed:
        raise RateLimitExceededError()

    response = await call_next(request)
    return response

async def logging_request_middleware(request: Request, call_next):
    response = await call_next(request)

    log = f"IP: {request.client.host if request.client else 'Unknown'} | {request.method} {request.url.path} | Status: {response.status_code}"
    logging.getLogger(__name__).info(log)

    return response