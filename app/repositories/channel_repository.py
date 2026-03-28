from app.models import Channel
from app.core.errors import InternalError
from .base_repository import BaseRepository
from app.interfaces import ChannelInterface

class ChannelRepository(BaseRepository, ChannelInterface):
    def get_channels(self, user_id: int) -> list[Channel]:
        query = """
            SELECT id, uuid, title, link, 
            EXISTS(
                SELECT 1 
                FROM disabled 
                WHERE consumer_id = %s AND channel_id = channel.id
            ) AS disabled_by_user
            FROM channel
        """
        params = (user_id, )
        db_result = self._execute(query=query, params=params)
        if not db_result.success or not db_result.data:
            raise InternalError(
                internal_message=f"Query created by get_channels failed because: {db_result.error_message if db_result.error_message else "There are no saved channels in DB"}."
            )

        try:
            return [Channel(**channel) for channel in db_result.data]
        except Exception as e:
            raise InternalError(
                internal_message=f"Mapping db result data to Channel objects failed in method get_channels because: {e}."
            )

    def set_disabled_channels(self, user_id: int, channel_ids: list[int]) -> None:
        inserts = [("DELETE FROM disabled WHERE consumer_id = %s", (user_id,))]
        query = """
            INSERT INTO disabled (consumer_id, channel_id) VALUES (%s, %s) 
        """
        for id in channel_ids:
            inserts.append((query, (user_id, id, )))

        result = self._execute_transaction(inserts)
        if not result.success:
            raise InternalError(
                internal_message=f"Query in set_unwanted_channels failed because: {result.error_message}"
            )

