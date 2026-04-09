import random
from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user
from app.dependencies.service_container import get_service_container
from fastapi.security import OAuth2PasswordRequestForm
from app.models import Consumer
from app.core.util import ServiceContainer
from app.schemas import RegistrationDTO, ConsumerDTO, UpdateCredentialsDTO
from app.core.errors import InternalError
from app.schemas.responses import ConsumersResponse, BaseResponse, TokenResponse
from dataclasses import asdict

consumer_router = APIRouter(
    prefix="/consumers",
    tags=["consumers"]
)

@consumer_router.post("/register/request_new_registration", response_model=BaseResponse)
def request_new_registration(registration: RegistrationDTO, services: ServiceContainer = Depends(get_service_container)):
    registration.password = services.security.get_password_hash(registration.password)
    services.db.is_username_or_email_used(username=registration.username, email=registration.email)

    is_pending = services.cache.is_registration_pending(registration)
    if is_pending:
        services.cache.delete_registration_from_pending(registration)

    code = random.randint(100000, 999999)
    services.email.send_verification_code(registration.email, code)
    services.cache.create_pending_registration(registration, code)

    return BaseResponse(
        success=True,
        message="New pending registration created.",
        status_code=200
    )

@consumer_router.post("/register/verify_email", response_model=TokenResponse)
def verify_email(email: str, code: int, services: ServiceContainer = Depends(get_service_container)):
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
        return TokenResponse(
            access_token=token,
            token_type="Bearer"
        )
    else:
        raise InternalError(status_code=400, public_message="Expired registration request or Invalid code.")

@consumer_router.post("/login", response_model=TokenResponse)
def login(login: OAuth2PasswordRequestForm = Depends(), services: ServiceContainer = Depends(get_service_container)):
    consumer: Consumer = services.db.get_consumer_by_credential(login.username)

    saved_hash = services.db.get_consumers_hash(consumer.id)
    services.security.verify_password(saved_hash, login.password)

    token = services.security.create_access_token(
        {
            "uuid": consumer.uuid,
            "username": consumer.username,
            "email": consumer.email
        }
    )
    return TokenResponse(
        access_token=token,
        token_type="Bearer"
    )

@consumer_router.get("/get_currently_logged_consumer", response_model=ConsumersResponse)
def get_currently_logged_consumer(current_user: Consumer = Depends(get_current_user)):
    return ConsumersResponse(
        status_code=200,
        success=True,
        message="Current user fetched successfully.",
        consumers = [ConsumerDTO(**asdict(current_user))]
    )

@consumer_router.put("/update_credentials", response_model=TokenResponse)
def update_credentials(request: UpdateCredentialsDTO, user: Consumer = Depends(get_current_user), services: ServiceContainer = Depends(get_service_container)):
    hash = services.db.get_consumers_hash(user.id)
    try:
        services.security.verify_password(hash, request.old_password)
    except InternalError:
        raise InternalError(
            status_code=400,
            public_message="Provided incorrect old password."
        )

    if request.new_username:
        consumer = services.db.get_consumer_by_username(request.new_username)
        if consumer:
            raise InternalError(
                status_code=400,
                public_message="User with provided username already exists."
            )

        services.db.update_consumers_username(user.id, request.new_username)

    if request.new_password:
        if services.security.is_password_identical_to_hash(hash, request.new_password):
            raise InternalError(
                status_code=400,
                public_message="Cannot change password with previously used password."
            )
        new_hash = services.security.get_password_hash(request.new_password)
        services.db.update_consumers_password(user.id, new_hash)

    token = services.security.create_access_token(
        {
            "uuid": user.uuid,
            "username": request.new_username if request.new_username else user.username,
            "email": user.email
        }
    )

    return TokenResponse(
        access_token=token,
        token_type="Bearer"
    )




