from typing import Optional
from app.models import AlreadyExistsEnum, Consumer, Channel, Article
from app.repositories import ChannelRepository, ConsumerRepository, ArticleRepository, LikesRepository
from app.schemas import RegistrationDTO

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
            raise Exception("Channels list cannot be empty.")
        
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
            raise Exception("Consumer not found by provided credential.")
        return consumer
    
    def get_consumers_hash(self, uuid: str) -> str:
        hash: str = self.consumers.get_consumers_hash(uuid)
        if not hash:
            raise Exception("No hash found for provided consumers UUID.")
        
        return hash
    
    def like_article(self, article_uuid: str, consumer_uuid: str) -> bool:
        try:
            article_id = self.articles.article_uuid_to_id(article_uuid)
        except Exception as e:
            raise e
        if not article_id:
            raise Exception(f"Article with public ID {article_uuid} not found.")
        
        consumer = self.consumers.get_consumer_by_uuid(consumer_uuid)
        if not consumer:
            raise Exception(f"Consumer with public ID {consumer_uuid} not found.")
        
        return self.likes.like_article(article_id=article_id, consumer_id=consumer.id)

