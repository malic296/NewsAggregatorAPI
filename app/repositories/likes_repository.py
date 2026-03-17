from .base_repository import BaseRepository
from app.interfaces.likes_interface import LikesInterface
from app.core.errors import InternalError

class LikesRepository(BaseRepository, LikesInterface):
    def like_article(self, article_id: int, consumer_id: int) -> bool:
        query = "SELECT * FROM likes WHERE article_id = %s and consumer_id = %s"
        params = (article_id, consumer_id,)
        result = self._execute(query, params)

        if not result.success:
            raise InternalError(
                internal_message=f"Failed selecting from likes table because: {result.error_message}",
                public_message="Liking articled failed due to server error."
            )
        if result.data:
            query = "DELETE FROM likes WHERE article_id = %s and consumer_id = %s"
            liked = False
        else:
            query = "INSERT INTO likes(article_id, consumer_id) VALUES(%s, %s)"
            liked = True

        result = self._execute(query, params)
        if not result.row_count or result.row_count == 0:
            raise InternalError(
                internal_message=f"Liking article resulted in no rows being changed.",
                public_message="Liking articled failed due to server error."
            )
        if not result.success:
            raise InternalError(
                internal_message=f"Failed liking article because: {result.error_message}",
                public_message="Liking articled failed due to server error."
            )
        
        return liked