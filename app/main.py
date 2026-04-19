from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import v1_router
from app.api.dependencies import generate_unique_endpoint_id
from app.core.container import ServiceContainer
from app.handlers import create_logging_handler
from app.repositories import ArticleRepository, ChannelRepository, ConsumerRepository
from app.services import CacheService, SecurityService, EmailService, ArticleService, ChannelService, ConsumerService
from app.core.settings import Settings
from app.core.middlewares import rate_limit_middleware, logging_request_middleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.handlers.exception_handler import global_exception_handler
from app.core.database import create_connection_pool

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # REPOSITORIES
    db_pool = create_connection_pool(settings)
    article_repository = ArticleRepository(connection_pool=db_pool)
    channel_repository = ChannelRepository(connection_pool=db_pool)
    consumer_repository = ConsumerRepository(connection_pool=db_pool)

    # UTIL SERVICES
    cache = CacheService(host=settings.valkey_host, port=settings.valkey_port, db=settings.valkey_db)
    security = SecurityService(pepper=settings.pepper, jwt=settings.jwt_secret)
    email = EmailService(resend_key=settings.resend_key)

    # CORE SERVICES
    article_service = ArticleService(articles=article_repository, cache=cache)
    channel_service = ChannelService(channels=channel_repository, cache=cache)
    consumer_service = ConsumerService(
        consumers=consumer_repository,
        cache=cache,
        security=security,
        email=email,
    )

    # LOGGER
    logger = create_logging_handler(db_pool)

    # DEPENDENCY CONTAINER
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

    # FREE RESOURCES
    db_pool.close()

# APP
app = FastAPI(debug=(settings.environment == "dev"), generate_unique_id_function=generate_unique_endpoint_id, lifespan=lifespan)

# EXCEPTION HANDLERS
app.add_exception_handler(Exception, global_exception_handler)

# MIDDLEWARES
app.add_middleware(BaseHTTPMiddleware, dispatch=rate_limit_middleware)
app.add_middleware(BaseHTTPMiddleware, dispatch=logging_request_middleware)
#app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "dev" else ["https://production.com"],
    allow_methods=["GET", "POST"]
)

# ROUTERS
app.include_router(v1_router)
