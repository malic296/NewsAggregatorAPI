from typing import Optional
from app.models import Consumer, Article
from app.repositories import ArticleRepository
from app.core.errors import ArticleNotFoundError
from .cache_service import CacheService

class ArticleService:
    def __init__(self, articles: ArticleRepository, cache: CacheService):
        self.articles = articles
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

    def like_article(self, article_uuid: str, consumer: Consumer) -> bool:
        article_id = self.articles.article_uuid_to_id(article_uuid)
        if not article_id:
            raise ArticleNotFoundError()

        return self.articles.like_article(article_id=article_id, consumer_id=consumer.id)