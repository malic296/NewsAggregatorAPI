from typing import Optional
from app.models import Channel
from app.models import Article
from app.models.enums.already_exists import AlreadyExistsEnum
from app.repositories import ChannelRepository, ConsumerRepository
from app.repositories import ArticleRepository

class DatabaseService:
    def __init__(self, channel_repository: ChannelRepository, article_repository: ArticleRepository, consumer_repository: ConsumerRepository):
        self.channels = channel_repository
        self.articles = article_repository
        self.consumers = consumer_repository

    def get_articles(self, hours: int = 1, channel_ids: Optional[list[int]] = None) -> list[Article]:
        if hours < 1:
            raise Exception('hours param must be same or greater than 1')
        return self.articles.get_articles(channel_ids=channel_ids, hours=hours)

    def get_channels(self) -> list[Channel]:
        return self.channels.get_channels()

    def is_username_or_email_used(self, username, email) -> Optional[AlreadyExistsEnum]:
        return self.consumers.is_username_or_email_used(username=username, email=email)
