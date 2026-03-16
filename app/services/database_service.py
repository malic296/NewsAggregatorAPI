from typing import Optional
from app.models import AlreadyExistsEnum, Consumer, Channel, Article
from app.repositories import ChannelRepository, ConsumerRepository, ArticleRepository, LikesRepository
from app.schemas import RegistrationDTO

class DatabaseService:
    def __init__(self):
        self.articles: ArticleRepository = ArticleRepository()
        self.channels: ChannelRepository = ChannelRepository()
        self.consumers: ConsumerRepository = ConsumerRepository()
        self.likes: LikesRepository = LikesRepository()

    def get_articles(self, consumer: Consumer, hours: int = 1, channel_ids: Optional[list[int]] = None) -> list[Article]:
        if hours < 1:
            raise Exception('hours param must be same or greater than 1')
        return self.articles.get_articles(consumer=consumer, channel_ids=channel_ids, hours=hours)

    def get_channels(self) -> list[Channel]:
        return self.channels.get_channels()

    def is_username_or_email_used(self, username, email) -> Optional[AlreadyExistsEnum]:
        return self.consumers.is_username_or_email_used(username=username, email=email)

    def register_consumer(self, registration: RegistrationDTO) -> Consumer:
        return self.consumers.register_consumer(registration)

    def get_consumer_by_email(self, email: str) -> Optional[Consumer]:
        return self.consumers.get_consumer_by_email(email)

    def get_consumer_by_username(self, username: str) -> Optional[Consumer]:
        return self.consumers.get_consumer_by_username(username)
    
    def get_consumer_by_credential(self, credential: str ) -> Optional[Consumer]:
        return self.consumers.get_consumer_by_credential(credential)
    
    def get_consumers_hash(self, uuid: str) -> str:
        return self.consumers.get_consumers_hash(uuid)
    
    def like_article(self, article_uuid: str, consumer_uuid: str) -> bool:
        try:
            article_id = self.articles.get_article_by_uuid(article_uuid)
            print(article_id)
        except Exception as e:
            raise e
        if not article_id:
            raise Exception(f"Article with public ID {article_uuid} not found.")
        
        consumer = self.consumers.get_consumer_by_uuid(consumer_uuid)
        if not consumer:
            raise Exception(f"Consumer with public ID {consumer_uuid} not found.")
        
        return self.likes.like_article(article_id=article_id, consumer_id=consumer.id)

