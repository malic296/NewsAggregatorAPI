from typing import Optional
from app.models import AlreadyExistsEnum, Consumer, Channel, Article, InternalError
from app.repositories import ChannelRepository, ConsumerRepository, ArticleRepository, LikesRepository
from app.schemas import RegistrationDTO
from fastapi import status

class DatabaseService:
    def __init__(self, articles: ArticleRepository, channels: ChannelRepository, consumers: ConsumerRepository, likes: LikesRepository):
        self.articles= articles
        self.channels= channels
        self.consumers= consumers
        self.likes= likes

    def get_articles(self, consumer: Consumer, hours: int = 1, channel_ids: Optional[list[int]] = None) -> list[Article]:
        return self.articles.get_articles(consumer=consumer, channel_ids=channel_ids, hours=hours)

    def get_channels(self) -> list[Channel]:
        channels: list[Channel] = self.channels.get_channels()
        if not channels:
            raise InternalError(
                internal_message="Available channels are not DB persistent. Update database.",
                public_message="Failed reading available channels because of inconsistent database."
            )
        
        return channels

    def is_username_or_email_used(self, username, email) -> Optional[AlreadyExistsEnum]:
        consumer: Consumer = self.consumers.get_consumer_by_username(username)
        if consumer:
            return AlreadyExistsEnum.USERNAME
        
        consumer: Consumer = self.consumers.get_consumer_by_email(email)
        if consumer:
            return AlreadyExistsEnum.EMAIL
        
        return None

    def register_consumer(self, registration: RegistrationDTO) -> Consumer:
        return self.consumers.register_consumer(registration)
    
    def get_consumer_by_credential(self, credential: str ) -> Consumer:
        consumer = self.consumers.get_consumer_by_username(credential)
        if not consumer:
            consumer = self.consumers.get_consumer_by_email(credential)

        if not consumer:
            raise InternalError(
                internal_message=f"Consumer not found by provided credential: {credential}.",
                public_message="Unable to retrieve users data by provided user credential.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        return consumer
    
    def get_consumers_hash(self, uuid: str) -> str:
        return self.consumers.get_consumers_hash(uuid)
    
    def like_article(self, article_uuid: str, consumer_uuid: str) -> bool:
        article_id = self.articles.article_uuid_to_id(article_uuid)
        consumer = self.consumers.get_consumer_by_uuid(consumer_uuid)
        
        return self.likes.like_article(article_id=article_id, consumer_id=consumer.id)

