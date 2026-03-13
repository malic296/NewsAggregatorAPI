from app.models.service_container import ServiceContainer
from app.repositories import ArticleRepository, ChannelRepository, ConsumerRepository
from app.services import DatabaseService
from app.services.cache_service import CacheService
from app.services.email_service import EmailService
from app.services.security_service import SecurityService

def get_service_container() -> ServiceContainer:
    return ServiceContainer(
        db=DatabaseService(
            article_repository=ArticleRepository(),
            channel_repository=ChannelRepository(),
            consumer_repository=ConsumerRepository()
        ),
        security=SecurityService(),
        cache=CacheService(),
        email=EmailService()
    )