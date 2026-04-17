from typing import Annotated
from fastapi import Depends, Request
from fastapi.routing import APIRoute
from fastapi.security import OAuth2PasswordBearer
from app.services import CacheService, DatabaseService, SecurityService, EmailService
from app.models import Consumer
from app.core.errors import AuthenticationRequiredError
from app.core.container import ServiceContainer
from app.handlers import LoggingHandler

def get_services(request: Request) -> ServiceContainer:
    return request.app.state.services

def get_database_service(services: Annotated[ServiceContainer, Depends(get_services)]) -> DatabaseService:
    return services.db

def get_security_service(services: Annotated[ServiceContainer, Depends(get_services)]) -> SecurityService:
    return services.security

def get_email_service(services: Annotated[ServiceContainer, Depends(get_services)]) -> EmailService:
    return services.email

def get_cache_service(services: Annotated[ServiceContainer, Depends(get_services)]) -> CacheService:
    return services.cache

def get_logger(services: Annotated[ServiceContainer, Depends(get_services)]) -> LoggingHandler:
    return services.logger

def generate_unique_endpoint_id(route: APIRoute):
    return route.name

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/consumers/login")

def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        security: Annotated[SecurityService, Depends(get_security_service)],
        db: Annotated[DatabaseService, Depends(get_database_service)]
    ) -> Consumer:

    payload = security.decode_access_token(token)
    if payload is None:
        raise AuthenticationRequiredError()

    user = db.get_consumer_by_credential(payload["username"])
    if not user:
        raise AuthenticationRequiredError()

    return user