from typing import Optional
from app.models import Consumer, Channel, Article
from app.core.errors import InternalError
from app.repositories import ChannelRepository, ConsumerRepository, ArticleRepository
from app.schemas import RegistrationDTO
from fastapi import status

class DatabaseService:
    def __init__(self, articles: ArticleRepository, channels: ChannelRepository, consumers: ConsumerRepository):
        self.articles= articles
        self.channels= channels
        self.consumers= consumers

    def get_articles(self, consumer: Consumer, hours: int = 1, channel_ids: Optional[list[int]] = None) -> list[Article]:
        return self.articles.get_articles(consumer=consumer, channel_ids=channel_ids, hours=hours)

    def get_channels(self) -> list[Channel]:
        return self.channels.get_channels()

    def is_username_or_email_used(self, username, email) -> None:
        consumer = self.consumers.get_consumer_by_username(username)
        if consumer:
            raise InternalError(
                public_message=f"Username already used: {username}.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        consumer = self.consumers.get_consumer_by_email(email)
        if consumer:
            raise InternalError(
                public_message=f"Email already used: {email}.",
                status_code=status.HTTP_400_BAD_REQUEST
            )


    def register_consumer(self, registration: RegistrationDTO) -> Consumer:
        return self.consumers.register_consumer(registration)
    
    def get_consumer_by_credential(self, credential: str ) -> Consumer:
        consumer = self.consumers.get_consumer_by_username(credential)
        if not consumer:
            consumer = self.consumers.get_consumer_by_email(credential)

        if not consumer:
            raise InternalError(
                public_message=f"No consumer found with provided credential: {credential}.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        return consumer
    
    def get_consumers_hash(self, id: int) -> str:
        hash = self.consumers.get_consumers_hash(id)
        if hash is None:
            raise InternalError(
                internal_message=f"No hash found for consumers id: {id}"
            )
        return hash
    
    def like_article(self, article_uuid: str, consumer: Consumer) -> bool:
        article_id = self.articles.article_uuid_to_id(article_uuid)
        if not article_id:
            raise InternalError(
                public_message=f"No article found for provided uuid: {article_uuid}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        return self.articles.like_article(article_id=article_id, consumer_id=consumer.id)

