from app.models import Channel, InternalError
from .base_repository import BaseRepository
from app.interfaces import ChannelInterface

class ChannelRepository(BaseRepository, ChannelInterface):
    def get_channels(self) -> list[Channel]:
        query = "SELECT * FROM channel ORDER BY id ASC"
        db_result = self._execute(query)
        if not db_result.success:
            raise InternalError(
                internal_message=f"Query created by get_channels failed because: {db_result.error_message}.",
                public_message=f"Reading available channels failed because of server error."
            )

        try:
            return [Channel(**channel) for channel in db_result.data]
        except Exception as e:
            raise InternalError(
                internal_message=f"Mapping db result data to Channel objects failed in method get_channels because: {db_result.error_message}.",
                public_message=f"Reading available channels failed because of server error."
            )
