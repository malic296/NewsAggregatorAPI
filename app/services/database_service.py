from typing import Optional
from app.models import Channel
from app.models import Article
from app.repositories import ChannelRepository
from app.repositories import ArticleRepository

class DatabaseService:
    def __init__(self, channel_repository: ChannelRepository, article_repository: ArticleRepository):
        self.channels = channel_repository
        self.articles = article_repository

    def get_articles(self, hours: int = 1, channel_ids: Optional[list[int]] = None) -> list[Article]:
        if hours < 1:
            raise Exception('hours param must be same or greater than 1')
        return self.articles.get_articles(channel_ids=channel_ids, hours=hours)

    def get_channels(self) -> list[Channel]:
        return self.channels.get_channels()
