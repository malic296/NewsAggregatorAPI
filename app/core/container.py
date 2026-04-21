from dataclasses import dataclass
from app.services import ArticleService, ChannelService, ConsumerService, EmailService, SecurityService, CacheService

@dataclass(frozen=True)
class ServiceContainer:
    article_service: ArticleService
    channel_service: ChannelService
    consumer_service: ConsumerService
    cache_service: CacheService
    email_service: EmailService
    security_service: SecurityService