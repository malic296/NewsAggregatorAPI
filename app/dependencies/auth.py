from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status
from typing import Annotated
from app.dependencies.service_container import get_service_container
from app.models import Consumer
from app.core.util import ServiceContainer
from app.core.errors import InternalError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/latest/consumers/login")

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], services: ServiceContainer = Depends(get_service_container)) -> Consumer:
    payload = services.security.decode_access_token(token)
    if payload is None:
        raise InternalError(
            public_message="You need to login or register first to use this endpoint.",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    return services.db.get_consumer_by_credential(payload["username"])