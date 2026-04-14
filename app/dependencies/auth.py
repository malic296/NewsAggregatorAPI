from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status, Request
from typing import Annotated
from fastapi_limiter.depends import RateLimiter
from app.dependencies.service_container import get_service_container
from app.models import Consumer
from app.core.util import ServiceContainer
from app.core.errors import InternalError
from pyrate_limiter import Limiter, Rate, Duration

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/latest/consumers/login")

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], services: ServiceContainer = Depends(get_service_container)) -> Consumer:
    payload = services.security.decode_access_token(token)
    if payload is None:
        raise InternalError(
            public_message="You need to login or register first to use this endpoint.",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    user = services.db.get_consumer_by_credential(payload["username"])
    if not user:
        raise InternalError(
            public_message="You need to login or register with a valid user first to use this endpoint.",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    return user

async def ip_identifier(request: Request):
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return f"{request.client.host}:shared-limit"

def get_rate_limiter() -> RateLimiter:
    return RateLimiter(
        limiter=Limiter(Rate(10, Duration.SECOND * 5)),
        identifier=ip_identifier
    )