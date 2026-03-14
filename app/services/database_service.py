from typing import Optional
from app.models import Channel
from app.models import Article
from app.models.enums.already_exists import AlreadyExistsEnum
from app.repositories import ChannelRepository, ConsumerRepository, ArticleRepository, LikesRepository
from app.models.consumer import Consumer
from app.schemas.registration_dto import RegistrationDTO

class DatabaseService:
    def __init__(self):
        self.articles: ArticleRepository = ArticleRepository()
        self.channels: ChannelRepository = ChannelRepository()
        self.consumers: ConsumerRepository = ConsumerRepository()
        self.likes: LikesRepository = LikesRepository()

    def get_articles(self, hours: int = 1, channel_ids: Optional[list[int]] = None) -> list[Article]:
        if hours < 1:
            raise Exception('hours param must be same or greater than 1')
        return self.articles.get_articles(channel_ids=channel_ids, hours=hours)

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
    
    def like_article(self, article_id: int, consumer_id: int) -> bool:
        return self.likes.like_article(article_id=article_id, consumer_id=consumer_id)

