from fastapi import APIRouter, Depends, HTTPException
from app.models.consumer import Consumer
from app.models.enums.already_exists import AlreadyExistsEnum
from app.schemas.registration_dto import RegistrationDTO
from app.models.service_container import ServiceContainer
import random
from app.dependencies.service_container import get_service_container
from app.schemas.login_dto import LoginDTO

consumer_router = APIRouter(
    prefix="/consumers",
    tags=["consumers"]
)

@consumer_router.post("/register/request_new_registration")
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

    return {"message" : "Registration created"}

@consumer_router.post("/register/verify_email")
def verify_email(email: str, code:int,  services: ServiceContainer = Depends(get_service_container)):
    registration = services.cache.provided_code_correct(email, code)
    if registration:
        consumer: Consumer = services.db.register_consumer(registration)
        token = services.security.create_access_token(
            {
                "usr": consumer.username,
                "email": consumer.email
            }
        )
        return {
            "message" : "Email verified",
            "token": token,
            "token_type": "Bearer"
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

@consumer_router.post("/login")
def login(login_request: LoginDTO, services: ServiceContainer = Depends(get_service_container)):
    if login_request.email:
        consumer: Consumer = services.db.get_consumer_by_email(login_request.email)

    elif login_request.username:
        consumer: Consumer = services.db.get_consumer_by_username(login_request.username)

    if not consumer:
        raise HTTPException(status_code=404, detail="User not found")

    if not services.security.verify_password(consumer.password, login_request.password):
        raise HTTPException(status_code=400, detail="Invalid password for provided email or username.")

    token = services.security.create_access_token(
        {
            "usr": consumer.username,
            "email": consumer.email
        }
    )
    return {
        "message": "Email verified",
        "token": token,
        "token_type": "Bearer"
    }



