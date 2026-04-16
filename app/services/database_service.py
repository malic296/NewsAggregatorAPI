from typing import Optional
from app.models import Consumer, Channel, Article
from app.core.errors import EmailAlreadyUsedError, UsernameAlreadyUsedError, RegistrationExpiredError, ArticleNotFoundError
from app.repositories import ChannelRepository, ConsumerRepository, ArticleRepository
from app.schemas import RegistrationDTO, ChannelDTO
from fastapi import status
from app.schemas import UpdateCredentialsDTO
from.cache_service import CacheService

class DatabaseService:
    def __init__(self, articles: ArticleRepository, channels: ChannelRepository, consumers: ConsumerRepository, cache: CacheService):
        self.articles = articles
        self.channels = channels
        self.consumers = consumers
        self.cache = cache

    def get_articles(self, consumer: Consumer, hours: int = 1) -> list[Article]:
        return self.articles.get_articles(consumer=consumer, hours=hours)

    def get_article(self, uuid: str) -> Optional[Article]:
        article = self.cache.get_article(uuid=uuid)
        if not article:
            article = self.articles.get_article(uuid=uuid)
            if article:
                self.cache.set_article(article=article)
        return article

    def get_channels(self, user_id: int) -> list[Channel]:
        cached_channels = self.cache.get_available_channels(user_id=user_id)
        if cached_channels:
            return cached_channels

        channels = self.channels.get_channels(user_id)
        self.cache.set_available_channels(channels=channels, user_id=user_id)
        return channels

    def set_disabled_channels(self, user_id: int, disabled_channels: list[ChannelDTO]) -> None:
        self.cache.invalidate_cache_channels(user_id=user_id)
        self.channels.set_disabled_channels_by_uuids(user_id, [channel.uuid for channel in disabled_channels])

    def is_email_used(self, email: str) -> bool:
        consumer = self.consumers.get_consumer_by_email(email)
        if consumer:
            return True

        return False

    def is_username_used(self, username: str) -> bool:
        consumer = self.consumers.get_consumer_by_username(username)
        if consumer:
            return True

        return False

    def validate_new_registration(self, registration: RegistrationDTO) -> None:
        consumer = self.consumers.get_consumer_by_email(email=registration.email)
        if consumer:
            raise EmailAlreadyUsedError()

        consumer = self.consumers.get_consumer_by_username(username=registration.username)
        if consumer:
            raise UsernameAlreadyUsedError()

    def create_new_registration(self, registration: RegistrationDTO, code: int) -> None:
        is_pending = self.cache.is_registration_pending(registration)
        if is_pending:
            self.cache.delete_registration_from_pending(registration)

        self.cache.create_pending_registration(registration, code)

    def register_consumer(self, email: str, code: int) -> Consumer:
        registration = self.cache.provided_code_correct(email=email, code=code)
        if registration:
            return self.consumers.register_consumer(registration)
        else:
            raise RegistrationExpiredError()
    
    def get_consumer_by_credential(self, credential: str) -> Optional[Consumer]:
        consumer = self.consumers.get_consumer_by_username(credential)
        if not consumer:
            consumer = self.consumers.get_consumer_by_email(credential)

        return consumer

    def get_consumer_by_username(self, username: str) -> Optional[Consumer]:
        return self.consumers.get_consumer_by_username(username)
    
    def get_consumers_hash(self, id: int) -> Optional[str]:
        return self.consumers.get_consumers_hash(id)
    
    def like_article(self, article_uuid: str, consumer: Consumer) -> bool:
        article_id = self.articles.article_uuid_to_id(article_uuid)
        if not article_id:
            raise ArticleNotFoundError()
        
        return self.articles.like_article(article_id=article_id, consumer_id=consumer.id)

    def update_credentials(self, request: UpdateCredentialsDTO, user: Consumer):
        if request.new_username:
            self.consumers.update_consumers_username(user_id=user.id, new_username=request.new_username)
            user.username = request.new_username

        if request.new_password:
            self.consumers.update_consumers_password(user_id=user.id, new_hash=request.new_password)

        return user