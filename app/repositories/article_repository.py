from typing import Optional
from app.models import Article
from .base_repository import BaseRepository
from app.interfaces.article_interface import ArticleInterface
from datetime import datetime, timezone, timedelta

class ArticleRepository(BaseRepository, ArticleInterface):
    def get_articles(self, channel_ids: Optional[list[int]] = None, hours: int = 1) -> list[Article]:
        if channel_ids is None or not isinstance(channel_ids, list) or len(channel_ids) == 0 :
            query = "SELECT * FROM article WHERE pub_date >= %s ORDER BY pub_date DESC"
            params = (datetime.now(timezone.utc) - timedelta(hours=hours),)

        else:
            query = "SELECT * FROM article WHERE channel_id = ANY(%s) AND pub_date >= %s ORDER BY pub_date DESC"
            params = (channel_ids, datetime.now(timezone.utc) - timedelta(hours=hours),)
        db_result = self._execute(query, params)
        if not db_result.success:
            raise Exception(f"Failed getting articles because: {e}")

        try:
            return [Article(**article) for article in db_result.data]
        except Exception as e:
            raise e