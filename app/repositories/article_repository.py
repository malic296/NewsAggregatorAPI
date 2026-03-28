from typing import Optional
from .base_repository import BaseRepository
from app.interfaces.article_interface import ArticleInterface
from datetime import datetime, timezone, timedelta
from app.models import Consumer, Article
from app.core.errors import InternalError

class ArticleRepository(BaseRepository, ArticleInterface):
    def get_articles(self, consumer: Consumer, hours: int = 1) -> list[Article]:
        query = """
                SELECT 
                    a.id, a.uuid, a.title, a.description, a.link, a.pub_date, 
                    c.link AS channel_link, 
                    COUNT(l.id) as likes,
                    EXISTS (
                        SELECT 1 FROM likes 
                        WHERE article_id = a.id AND consumer_id = %s
                    ) AS liked_by_user    
                FROM article AS a 
                JOIN channel AS c ON c.id = a.channel_id
                LEFT JOIN likes AS l ON a.id = l.article_id
                WHERE a.pub_date >= %s
                  -- THIS IS THE REVERSED LOGIC:
                  AND a.channel_id NOT IN (
                      SELECT channel_id FROM disabled WHERE consumer_id = %s
                  )
                GROUP BY a.id, c.link 
                ORDER BY a.pub_date DESC
            """

        since_date = datetime.now(timezone.utc) - timedelta(hours=hours)

        params = (consumer.id, since_date, consumer.id)

        db_result = self._execute(query, params)

        if not db_result.success:
            raise InternalError(
                internal_message=f"Failed getting articles: {db_result.error_message}"
            )

        try:
            return [Article(**article) for article in db_result.data]
        except Exception as e:
            raise InternalError(
                internal_message=f"Mapping failed: {e}"
            )

    def article_uuid_to_id(self, article_uuid: str) -> Optional[int]:
        query = "SELECT id FROM article WHERE uuid = %s"
        db_result = self._execute(query, (article_uuid,))

        if not db_result.success:
            raise InternalError(
                internal_message=f"Query created by article_uuid_to_id failed because: {db_result.error_message}"
            )

        if not db_result.data:
            return None

        try:
            return db_result.data[0]["id"]
        except Exception as e:
            raise InternalError(
                internal_message=f"Method article_uuid_to_id failed because invalid data format: {e}."
            )

    def like_article(self, article_id: int, consumer_id: int) -> bool:
        query = """
            SELECT 1 FROM likes where article_id = %s AND consumer_id = %s
        """
        params = (article_id, consumer_id,)
        db_result = self._execute(query, params)
        if not db_result.success:
            raise InternalError(
                internal_message=f"Method like_article failed initial select because: {db_result.error_message}."
            )

        if not db_result.data:
            query = "INSERT INTO likes(article_id, consumer_id) VALUES (%s, %s)"
            liked = True
        else:
            query = "DELETE FROM likes WHERE article_id = %s AND consumer_id = %s"
            liked = False

        db_result = self._execute(query, params)

        if not db_result.success:
            raise InternalError(
                internal_message=f"Method like_article failed like logic because: {db_result.error_message}."
            )

        if not db_result.row_count > 0:
            raise InternalError(
                internal_message=f"Method like_article did not change any rows."
            )

        return liked