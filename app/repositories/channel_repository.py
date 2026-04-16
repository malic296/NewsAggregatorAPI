from app.models import Channel
from app.core.errors import DatabaseError, MappingError
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
            raise DatabaseError(
                message=db_result.error_message if db_result.error_message else "Unknown error",
                method="get_channels"
            )

        try:
            return [Channel(**channel) for channel in db_result.data]
        except Exception as e:
            raise MappingError(mapping_error=str(e), method="get_channels")

    def set_disabled_channels_by_uuids(self, user_id: int, disabled_uuids: list[str]) -> None:
        inserts = [("DELETE FROM disabled WHERE consumer_id = %s", (user_id,))]

        query = """
            INSERT INTO disabled (consumer_id, channel_id) 
            SELECT %s, id
            FROM channel
            WHERE uuid = ANY(%s)
        """

        inserts.append((query, (user_id, disabled_uuids, )))

        db_result = self._execute_transaction(inserts)
        if not db_result.success:
            raise DatabaseError(
                message=db_result.error_message if db_result.error_message else "Unknown error",
                method="set_disabled_channels_by_uuids"
            )

