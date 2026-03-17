from app.core.util import ServiceContainer
from app.services import DatabaseService, CacheService, EmailService, SecurityService
from app.repositories import ArticleRepository, ChannelRepository, ConsumerRepository, LikesRepository

def get_service_container() -> ServiceContainer:
    return ServiceContainer(
        db=DatabaseService(
            articles = ArticleRepository(),
            channels= ChannelRepository(),
            consumers = ConsumerRepository(),
            likes = LikesRepository()
        ),
        security=SecurityService(),
        cache=CacheService(),
        email=EmailService()
    )