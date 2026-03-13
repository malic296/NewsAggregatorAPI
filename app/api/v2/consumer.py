from fastapi import APIRouter, Depends
from app.models.enums.already_exists import AlreadyExistsEnum
from app.repositories import ArticleRepository, ChannelRepository, ConsumerRepository
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

@consumer_router.post("/consumers/register/request_new_registration")
def request_new_registration(registration: RegistrationDTO, services: ServiceContainer = Depends(get_service_container)):
    registration.password = services.security.get_password_hash(registration.password)
    is_used_by = services.db.is_username_or_email_used(username=registration.username, email=registration.email)
    match is_used_by:
        case AlreadyExistsEnum.EMAIL:
            raise Exception("Email already used")
        case AlreadyExistsEnum.USERNAME:
            raise Exception("Username already used")
        case _:
            is_pending = services.cache.is_registration_pending(registration)
            if is_pending:
                services.cache.delete_registration_from_pending(registration)

            code = random.randint(100000, 999999)
            services.email.send_verification_code(registration.email, code)
            services.cache.create_pending_registration(registration, code)

    return {"message" : "Registration created"}

@consumer_router.post("/consumers/register/verify_email_registration")
def verify_email_registration(email: str, code:int,  services: ServiceContainer = Depends(get_service_container)):
    registration = services.cache.provided_code_correct(email, code)
    if registration:
        services.db.register_user(registration)
        return {"message" : "Email verified"}
    else:
        raise Exception("Email not yet registered or code is incorrect")