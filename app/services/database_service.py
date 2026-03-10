from app.models import Channel
from app.models import Article
from app.repositories import ChannelRepository
from app.repositories import ArticleRepository

class DatabaseService:
    def __init__(self, channel_repository: ChannelRepository, article_repository: ArticleRepository):
        self.channels = channel_repository
        self.articles = article_repository

    def get_articles(self) -> list[Article]:
        return self.articles.get_articles()

    def get_articles_by_channels(self, channel_ids: list[int]) -> list[Article]:
        return self.articles.get_articles_by_channels(channel_ids)

    def get_channels(self) -> list[Channel]:
        return self.channels.get_channels()
