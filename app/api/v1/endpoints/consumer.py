from fastapi import APIRouter, Depends
from app.api.dependencies import get_consumer_service, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from app.models import Consumer
from app.schemas import RegistrationDTO, ConsumerDTO, UpdateCredentialsDTO
from app.schemas.responses import ConsumerResponse, BaseResponse, TokenResponse
from dataclasses import asdict

consumer_router = APIRouter(
    prefix="/consumers",
    tags=["consumers"]
)

@consumer_router.post("/register", response_model=BaseResponse)
def register(registration: RegistrationDTO, consumer_service = Depends(get_consumer_service)):
    consumer_service.request_registration(registration)
    return BaseResponse(
        success=True,
        message="New pending registration created."
    )

@consumer_router.post("/verification", response_model=TokenResponse)
def verification(email: str, code: int, consumer_service = Depends(get_consumer_service)):
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

@consumer_router.get("/me", response_model=ConsumerResponse)
def me(current_user: Consumer = Depends(get_current_user)):
    return ConsumerResponse(
        success=True,
        message="Current user fetched successfully.",
        consumer = ConsumerDTO(**asdict(current_user))
    )

@consumer_router.put("/credentials", response_model=TokenResponse)
def credentials(request: UpdateCredentialsDTO, user: Consumer = Depends(get_current_user), consumer_service = Depends(get_consumer_service)):
    token = consumer_service.update_credentials_and_issue_token(request, user)
    return TokenResponse(
        access_token=token,
        token_type="Bearer"
    )



