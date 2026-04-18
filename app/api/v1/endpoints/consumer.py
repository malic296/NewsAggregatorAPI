from fastapi import APIRouter, Depends
from app.api.dependencies import get_consumer_service, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from app.models import Consumer
from app.schemas import RegistrationDTO, ConsumerDTO, UpdateCredentialsDTO
from app.schemas.responses import ConsumersResponse, BaseResponse, TokenResponse
from dataclasses import asdict

consumer_router = APIRouter(
    prefix="/consumers",
    tags=["consumers"]
)

@consumer_router.post("/register/request_new_registration", response_model=BaseResponse)
def request_new_registration(registration: RegistrationDTO, consumer_service = Depends(get_consumer_service)):
    consumer_service.request_registration(registration)
    return BaseResponse(
        success=True,
        message="New pending registration created."
    )

@consumer_router.post("/register/verify_email", response_model=TokenResponse)
def verify_email(email: str, code: int, consumer_service = Depends(get_consumer_service)):
    token = consumer_service.verify_registration(email=email, code=code)
    return TokenResponse(
        access_token=token,
        token_type="Bearer"
    )

@consumer_router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), consumer_service = Depends(get_consumer_service)):
    token = consumer_service.authenticate(form.username, form.password)
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
def update_credentials(request: UpdateCredentialsDTO, user: Consumer = Depends(get_current_user), consumer_service = Depends(get_consumer_service)):
    token = consumer_service.update_credentials_and_issue_token(request, user)
    return TokenResponse(
        access_token=token,
        token_type="Bearer"
    )



