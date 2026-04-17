from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import v1_router
from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.handlers import LoggingHandler
from app.schemas.responses import BaseResponse
from app.api.dependencies import generate_unique_endpoint_id
from app.core.errors import RateLimitExceededError, AppError
from app.core.container import ServiceContainer
from app.handlers import create_logging_handler
from app.repositories import ArticleRepository, ChannelRepository, ConsumerRepository
from app.services import CacheService, SecurityService, EmailService, ArticleService, ChannelService, ConsumerService

@asynccontextmanager
async def lifespan(app: FastAPI):
    cache = CacheService()
    security = SecurityService()
    email = EmailService()
    article_service = ArticleService(articles=ArticleRepository(), cache=cache)
    channel_service = ChannelService(channels=ChannelRepository(), cache=cache)
    consumer_service = ConsumerService(consumers=ConsumerRepository(), cache=cache)

    logger = create_logging_handler()

    app.state.services = ServiceContainer(
        article_service=article_service,
        channel_service=channel_service,
        consumer_service=consumer_service,
        cache_service=cache,
        email_service=email,
        security_service=security,
        logger=logger
    )
    yield
app = FastAPI(debug=True, generate_unique_id_function=generate_unique_endpoint_id, lifespan=lifespan)

def create_error_response(err: AppError) -> JSONResponse:
    response: BaseResponse = BaseResponse(
        success=False,
        message=err.public_message
    )

    return JSONResponse(
        status_code=err.status_code,
        content=response.model_dump()
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, err: Exception):
    logger: LoggingHandler = request.app.state.services.logger

    if isinstance(err, AppError):
        if err.internal_message:
            logger.handle(err.internal_message)

        return create_error_response(err=err)

    else:
        logger.handle(f"Unexpected Error: {str(err)} | Path: {request.url.path}")
        return create_error_response(
            AppError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                public_message=f"Server failed unexpectedly. Try again in a moment."
            )
        )

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    authorization_header = request.headers.get("Authorization")
    if authorization_header:
        client_key = authorization_header.removeprefix("Bearer").strip()
    else:
        client_key = request.client.host if request.client else "unknown"
    allowed = request.app.state.services.cache.can_request_go_through(client_key)
    if not allowed:
        err = RateLimitExceededError()
        return create_error_response(err)

    response = await call_next(request)
    return response

@app.middleware("http")
async def logging_request_middleware(request: Request, call_next):
    response = await call_next(request)

    log = f"IP: {request.client.host if request.client else 'Unknown'} | {request.method} {request.url.path} | Status: {response.status_code}"
    request.app.state.services.logger.handle(log)

    return response

#app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"]
)
app.include_router(v1_router)
