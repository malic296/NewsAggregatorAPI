import random
from fastapi import APIRouter, Depends, HTTPException
from app.dependencies.auth import get_current_user
from app.dependencies.service_container import get_service_container
from fastapi.security import OAuth2PasswordRequestForm
from app.models import Consumer
from app.core.enums import AlreadyExistsEnum
from app.core.util import ServiceContainer
from app.schemas import RegistrationDTO, ResponseDTO, ConsumerDTO

consumer_router = APIRouter(
    prefix="/consumers",
    tags=["consumers"]
)

@consumer_router.post("/register/request_new_registration", response_model=ResponseDTO[None])
def request_new_registration(registration: RegistrationDTO, services: ServiceContainer = Depends(get_service_container)):
    registration.password = services.security.get_password_hash(registration.password)
    is_used_by = services.db.is_username_or_email_used(username=registration.username, email=registration.email)
    match is_used_by:
        case AlreadyExistsEnum.EMAIL:
            raise HTTPException(status_code=400, detail="Email already used")
        case AlreadyExistsEnum.USERNAME:
            raise HTTPException(status_code=400, detail="Username already used")
        case _:
            is_pending = services.cache.is_registration_pending(registration)
            if is_pending:
                services.cache.delete_registration_from_pending(registration)

            code = random.randint(100000, 999999)
            services.email.send_verification_code(registration.email, code)
            services.cache.create_pending_registration(registration, code)

    return ResponseDTO(
        success=True,
        message="New pending registration created.",
        status_code=200
    )

@consumer_router.post("/register/verify_email")
def verify_email(email: str, code:int,  services: ServiceContainer = Depends(get_service_container)):
    registration = services.cache.provided_code_correct(email, code)
    if registration:
        consumer: Consumer = services.db.register_consumer(registration)
        token = services.security.create_access_token(
            {
                "uuid": consumer.uuid,
                "username": consumer.username,
                "email": consumer.email
            }
        )
        return {
            "access_token": token,
            "token_type": "Bearer"
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

@consumer_router.post("/login")
def login(login: OAuth2PasswordRequestForm = Depends(), services: ServiceContainer = Depends(get_service_container)):
    consumer: Consumer = services.db.get_consumer_by_credential(login.username)
    if not consumer:
        raise HTTPException(status_code=400, detail="Incorrect login details.")

    saved_hash = services.db.get_consumers_hash(consumer.uuid)

    if not services.security.verify_password(saved_hash, login.password):
        raise HTTPException(status_code=400, detail="Incorrect login details.")

    token = services.security.create_access_token(
        {
            "uuid": consumer.uuid,
            "username": consumer.username,
            "email": consumer.email
        }
    )
    return {
        "access_token": token,
        "token_type": "Bearer"
    }

@consumer_router.post("/get_currently_logged_consumer", response_model=ResponseDTO[ConsumerDTO])
def get_currently_logged_consumer(current_user = Depends(get_current_user), services: ServiceContainer = Depends(get_service_container)):

    return ResponseDTO(
        status_code=200,
        success=True,
        message="Current user fetched successful.",
        data = current_user
    )



