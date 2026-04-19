from app.core.errors import RateLimitExceededError
from app.handlers.exception_handler import create_error_response
from fastapi import Request

async def rate_limit_middleware(request: Request, call_next):
    authorization_header = request.headers.get("Authorization")
    if authorization_header:
        client_key = authorization_header.removeprefix("Bearer").strip()
    else:
        client_key = request.client.host if request.client else "unknown"
    allowed = request.app.state.services.cache_service.can_request_go_through(client_key)
    if not allowed:
        err = RateLimitExceededError()
        return create_error_response(err)

    response = await call_next(request)
    return response

async def logging_request_middleware(request: Request, call_next):
    response = await call_next(request)

    log = f"IP: {request.client.host if request.client else 'Unknown'} | {request.method} {request.url.path} | Status: {response.status_code}"
    request.app.state.services.logger.handle(log)

    return response