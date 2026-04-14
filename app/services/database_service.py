from typing import Optional
from app.models import Consumer, Channel, Article
from app.core.errors import InternalError
from app.repositories import ChannelRepository, ConsumerRepository, ArticleRepository
from app.schemas import RegistrationDTO, ChannelDTO
from fastapi import status

class DatabaseService:
    def __init__(self, articles: ArticleRepository, channels: ChannelRepository, consumers: ConsumerRepository):
        self.articles= articles
        self.channels= channels
        self.consumers= consumers

    def get_articles(self, consumer: Consumer, hours: int = 1) -> list[Article]:
        return self.articles.get_articles(consumer=consumer, hours=hours)

    def get_article(self, uuid: str):
        return self.articles.get_article(uuid)

    def get_channels(self, user_id: int) -> list[Channel]:
        return self.channels.get_channels(user_id)

    def set_disabled_channels(self, user_id: int, disabled_channels: list[ChannelDTO]) -> None:
        return self.channels.set_disabled_channels_by_uuids(user_id, [channel.uuid for channel in disabled_channels])

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

    def register_consumer(self, registration: RegistrationDTO) -> Consumer:
        return self.consumers.register_consumer(registration)
    
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
            raise InternalError(
                public_message=f"No article found for provided uuid: {article_uuid}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        return self.articles.like_article(article_id=article_id, consumer_id=consumer.id)

    def update_consumers_username(self, user_id: int, new_username: str) -> None:
        self.consumers.update_consumers_username(user_id=user_id, new_username=new_username)

    def update_consumers_password(self, user_id: int, new_hash: str) -> None:
        self.consumers.update_consumers_password(user_id=user_id, new_hash=new_hash)

