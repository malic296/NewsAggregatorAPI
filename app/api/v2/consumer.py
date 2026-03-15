from fastapi import APIRouter, Depends, HTTPException
from app.dependencies.auth import get_current_user
from app.models.consumer import Consumer
from app.models.enums.already_exists import AlreadyExistsEnum
from app.schemas.consumer_dto import ConsumerDTO
from app.schemas.registration_dto import RegistrationDTO
from app.models.service_container import ServiceContainer
import random
from app.dependencies.service_container import get_service_container
from app.schemas import LoginDTO, ResponseDTO
from fastapi.security import OAuth2PasswordRequestForm

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
                "id": consumer.id,
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
    consumer: Consumer = services.db.get_consumer_by_username(login.username)
    if not consumer:
        consumer: Consumer = services.db.get_consumer_by_email(login.username)

    if not consumer or not services.security.verify_password(consumer.password, login.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = services.security.create_access_token(
        {
            "id": consumer.id,
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
    consumer = services.db.get_consumer_by_creadential(current_user["username"])
    if not consumer:
        raise Exception("User is authorized but cannot get currently logged user.")
    
    return ResponseDTO(
        status_code=200,
        success=True,
        message="Current user fetched successful.",
        data = consumer
    )



