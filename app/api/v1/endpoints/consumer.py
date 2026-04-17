import random
from fastapi import APIRouter, Depends
from app.api.dependencies import get_email_service, get_consumer_service, get_current_user, get_security_service
from fastapi.security import OAuth2PasswordRequestForm
from app.models import Consumer
from app.schemas import RegistrationDTO, ConsumerDTO, UpdateCredentialsDTO
from app.core.errors import InvalidCredentialsError, InvalidCurrentPasswordError, PasswordReuseError
from app.schemas.responses import ConsumersResponse, BaseResponse, TokenResponse
from dataclasses import asdict

consumer_router = APIRouter(
    prefix="/consumers",
    tags=["consumers"]
)

@consumer_router.post("/register/request_new_registration", response_model=BaseResponse)
def request_new_registration(registration: RegistrationDTO, email_service = Depends(get_email_service), consumer_service = Depends(get_consumer_service), security = Depends(get_security_service)):
    registration.password = security.get_password_hash(registration.password)
    consumer_service.validate_new_registration(registration)
    code = random.randint(100000, 999999)
    email_service.send_verification_code(registration.email, code)
    consumer_service.create_new_registration(registration, code)

    return BaseResponse(
        success=True,
        message="New pending registration created."
    )

@consumer_router.post("/register/verify_email", response_model=TokenResponse)
def verify_email(email: str, code: int, consumer_service = Depends(get_consumer_service), security_service = Depends(get_security_service)):
    consumer: Consumer = consumer_service.register_consumer(email=email, code=code)
    token = security_service.create_access_token(consumer)
    return TokenResponse(
        access_token=token,
        token_type="Bearer"
    )

@consumer_router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), consumer_service = Depends(get_consumer_service), security_service = Depends(get_security_service)):
    consumer = consumer_service.get_consumer_by_credential(form.username)
    if not consumer or not security_service.verify_password(consumer_service.get_consumers_hash(consumer.id), form.password):
        raise InvalidCredentialsError()

    token = security_service.create_access_token(consumer)

    return TokenResponse(
        access_token=token,
        token_type="Bearer"
    )

@consumer_router.get("/get_currently_logged_consumer", response_model=ConsumersResponse)
def get_currently_logged_consumer(current_user: Consumer = Depends(get_current_user)):
    return ConsumersResponse(
        success=True,
        message="Current user fetched successfully.",
        consumers = [ConsumerDTO(**asdict(current_user))]
    )

@consumer_router.put("/update_credentials", response_model=TokenResponse)
def update_credentials(request: UpdateCredentialsDTO, user: Consumer = Depends(get_current_user), consumer_service = Depends(get_consumer_service), security_service = Depends(get_security_service)):
    if not security_service.verify_password(consumer_service.get_consumers_hash(user.id), request.old_password):
        raise InvalidCurrentPasswordError()

    if request.new_password:
        if security_service.is_password_identical_to_hash(consumer_service.get_consumers_hash(user.id), request.new_password):
            raise PasswordReuseError()
        request.new_password = security_service.get_password_hash(request.new_password)

    consumer: Consumer = consumer_service.update_credentials(request, user)

    token = security_service.create_access_token(consumer)

    return TokenResponse(
        access_token=token,
        token_type="Bearer"
    )




