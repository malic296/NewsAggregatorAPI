from pathlib import Path
from typing import Optional, Annotated
from fastapi import Depends, status
from fastapi.routing import APIRoute
from fastapi.security import OAuth2PasswordBearer
from app.handlers import LoggingHandler, DatabaseLogger, FileLogger
from app.repositories import ArticleRepository, ChannelRepository, ConsumerRepository, LoggingRepository
from app.services import CacheService, DatabaseService, SecurityService, EmailService, LoggingService
from app.core.errors import InternalError
from app.models import Consumer

def get_logging_handler(path: Optional[Path] = None, repo: Optional[LoggingRepository] = None) -> LoggingHandler:
    log_service: LoggingService = LoggingService(
        file_path = path if path else Path(__file__).parent.parent.parent / "api_errors.log",
        logging_repository = repo if repo else LoggingRepository()
    )

    db_logger = DatabaseLogger(log_service)
    file_logger = FileLogger(log_service)
    db_logger.set_next(file_logger)

    return db_logger

def get_database_service():
    cache = CacheService()
    return DatabaseService(
        articles=ArticleRepository(),
        channels=ChannelRepository(),
        consumers=ConsumerRepository(),
        cache=cache
    )

def get_security_service():
    return SecurityService()

def get_email_service():
    return EmailService()

def generate_unique_endpoint_id(route: APIRoute):
    return route.name


def get_current_user(token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="/v1/consumers/login"))], security = Depends(get_security_service), db = Depends(get_database_service)) -> Consumer:

    payload = security.decode_access_token(token)
    if payload is None:
        raise InternalError(
            public_message="You need to login or register first to use this endpoint.",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    user = db.get_consumer_by_credential(payload["username"])
    if not user:
        raise InternalError(
            public_message="You need to login or register with a valid user first to use this endpoint.",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    return user