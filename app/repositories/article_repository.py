from typing import Optional
from app.models import Article
from .base_repository import BaseRepository
from app.interfaces.article_interface import ArticleInterface
from datetime import datetime, timezone, timedelta
from app.models.consumer import Consumer

class ArticleRepository(BaseRepository, ArticleInterface):
    def get_articles(self, consumer: Consumer, channel_ids: Optional[list[int]] = None, hours: int = 1) -> list[Article]:
        query = """
            SELECT 
            a.id AS id, a.uuid AS uuid, a.title AS title, a.description AS description, a.link AS link, a.pub_date AS pub_date, c.link AS channel_link, COUNT(l.id) as likes,
            EXISTS (
                SELECT 1 FROM likes 
                WHERE article_id = a.id AND consumer_id = %s
            ) AS liked_by_user    
            FROM article AS a 
            LEFT JOIN likes AS l ON 
            a.id = l.article_id
            JOIN channel AS c ON
            c.id = a.channel_id
        """
        if channel_ids is None or not isinstance(channel_ids, list) or len(channel_ids) == 0 :
            query = query + " WHERE a.pub_date >= %s GROUP BY a.id, c.link ORDER BY a.pub_date DESC"
            params = (consumer.id, datetime.now(timezone.utc) - timedelta(hours=hours),)

        else:
            query = query + " WHERE a.channel_id = ANY(%s) AND a.pub_date >= %s GROUP BY a.id, c.link ORDER BY a.pub_date DESC"
            params = (consumer.id, channel_ids, datetime.now(timezone.utc) - timedelta(hours=hours),)
        db_result = self._execute(query, params)
        if not db_result.success:
            raise Exception(f"Failed getting articles because: {db_result.error_message}")

        try:
            return [Article(**article) for article in db_result.data]
        except Exception as e:
            raise e
        
    def get_article_by_uuid(self, article_uuid: str) -> Optional[int]:
        query = "SELECT id FROM article WHERE uuid = %s"
        db_result = self._execute(query, (article_uuid,))

        if not db_result.success:
            raise Exception(f"Database query failed: {db_result.error_message}")

        if not db_result.data or len(db_result.data) == 0:
            return None

        return db_result.data[0]["id"]