from app.models import Article
from .base_repository import BaseRepository
from app.interfaces.article_interface import ArticleInterface

class ArticleRepository(BaseRepository, ArticleInterface):
    def get_articles(self) -> list[Article]:
        query = "SELECT * FROM article ORDER BY pub_date DESC"
        db_result = self._execute(query)

        try:
            articles: list[Article] = [Article(**article) for article in db_result]
        except Exception as e:
            raise e
        return articles

    def get_articles_by_channels(self, channel_ids: list[int]) -> list[Article]:
        query = "SELECT * FROM article WHERE channel_id = ANY(%s) ORDER BY pub_date DESC"
        params = (channel_ids, )
        db_result = self._execute(query, params)

        try:
            articles: list[Article] = [Article(**article) for article in db_result]
        except Exception as e:
            raise e
        return articles