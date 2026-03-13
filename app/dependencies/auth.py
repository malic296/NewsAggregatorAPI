from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from typing import Annotated
from app.dependencies.service_container import get_service_container
from app.models.service_container import ServiceContainer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="consumers/login")

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], services: ServiceContainer = Depends(get_service_container)):
    payload = services.security.decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload