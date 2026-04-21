from typing import Annotated
from fastapi import Depends, Request
from fastapi.routing import APIRoute
from fastapi.security import OAuth2PasswordBearer
from app.services import CacheService, ArticleService, ChannelService, ConsumerService, SecurityService, EmailService
from app.models import Consumer
from app.core.errors import AuthenticationRequiredError
from app.core.container import ServiceContainer

def get_services(request: Request) -> ServiceContainer:
    return request.app.state.services

def get_article_service(services: Annotated[ServiceContainer, Depends(get_services)]) -> ArticleService:
    return services.article_service

def get_channel_service(services: Annotated[ServiceContainer, Depends(get_services)]) -> ChannelService:
    return services.channel_service

def get_consumer_service(services: Annotated[ServiceContainer, Depends(get_services)]) -> ConsumerService:
    return services.consumer_service

def get_security_service(services: Annotated[ServiceContainer, Depends(get_services)]) -> SecurityService:
    return services.security_service

def get_email_service(services: Annotated[ServiceContainer, Depends(get_services)]) -> EmailService:
    return services.email_service

def get_cache_service(services: Annotated[ServiceContainer, Depends(get_services)]) -> CacheService:
    return services.cache_service

def generate_unique_endpoint_id(route: APIRoute):
    return route.name

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/consumers/login")

def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        security: Annotated[SecurityService, Depends(get_security_service)],
        consumers: Annotated[ConsumerService, Depends(get_consumer_service)]
    ) -> Consumer:

    payload = security.decode_access_token(token)
    if payload is None:
        raise AuthenticationRequiredError()

    user = consumers.get_consumer_by_credential(payload["username"])
    if not user:
        raise AuthenticationRequiredError()

    return user