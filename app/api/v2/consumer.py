from fastapi import APIRouter, Depends
from app.repositories import ArticleRepository, ChannelRepository, ConsumerRepository
from app.schemas import ArticleDTO
from app.services import DatabaseService
from app.schemas.registration_dto import RegistrationDTO
from app.services.cache_service import CacheService
from app.services.email_service import EmailService
from app.services.security_service import SecurityService
from app.models.service_container import ServiceContainer
import random

consumer_router = APIRouter()

def get_service_container() -> ServiceContainer:
    return ServiceContainer(
        db=DatabaseService(
            article_repository=ArticleRepository(),
            channel_repository=ChannelRepository(),
            consumer_repository=ConsumerRepository()
        ),
        security=SecurityService(),
        cache=CacheService(),
        email=EmailService()
    )

@consumer_router.post("/consumers/register/validate_credentials", response_model=ArticleDTO)
def validate_credentials(registration: RegistrationDTO, services: ServiceContainer = Depends(get_service_container)):
    is_used_by = services.db.is_username_or_email_used(username=registration.username, email=registration.email)
    if is_used_by is None:
        registration.password = services.security.get_password_hash(registration.password)
        is_pending = services.cache.is_registration_pending(registration)
        if is_pending:
            services.cache.delete_registration_from_pending(registration)

        code = random.randint(100000, 999999)
        services.email.send_verification_code(registration.address, code)



@consumer_router.post("/consumers/register/validate_code", response_model=ArticleDTO)
def validate_code(email: str, code: int, services: ServiceContainer = Depends(get_service_container)):
    pass