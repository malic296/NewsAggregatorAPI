import random
from fastapi import APIRouter, Depends
from app.api.dependencies import get_email_service, get_database_service, get_current_user, get_security_service
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
def request_new_registration(registration: RegistrationDTO, email = Depends(get_email_service), db = Depends(get_database_service), security = Depends(get_security_service)):
    registration.password = security.get_password_hash(registration.password)
    db.validate_new_registration(registration)
    code = random.randint(100000, 999999)
    email.send_verification_code(registration.email, code)
    db.create_new_registration(registration, code)

    return BaseResponse(
        success=True,
        message="New pending registration created.",
        status_code=200
    )

@consumer_router.post("/register/verify_email", response_model=TokenResponse)
def verify_email(email: str, code: int, db = Depends(get_database_service), security = Depends(get_security_service)):
    consumer: Consumer = db.register_consumer(email=email, code=code)
    token = security.create_access_token(consumer)
    return TokenResponse(
        access_token=token,
        token_type="Bearer"
    )

@consumer_router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db = Depends(get_database_service), security = Depends(get_security_service)):
    consumer = db.get_consumer_by_credential(form.username)
    if not consumer or not security.verify_password(db.get_consumers_hash(consumer.id), form.password):
        raise InvalidCredentialsError()

    token = security.create_access_token(consumer)

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
def update_credentials(request: UpdateCredentialsDTO, user: Consumer = Depends(get_current_user), db = Depends(get_database_service), security = Depends(get_security_service)):
    if not security.verify_password(db.get_consumers_hash(user.id), request.old_password):
        raise InvalidCurrentPasswordError()

    if request.new_password:
        if security.is_password_identical_to_hash(db.get_consumers_hash(user.id), request.new_password):
            raise PasswordReuseError()
        request.new_password = security.get_password_hash(request.new_password)

    consumer: Consumer = db.update_credentials(request, user)

    token = security.create_access_token(consumer)

    return TokenResponse(
        access_token=token,
        token_type="Bearer"
    )




