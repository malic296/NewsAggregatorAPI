from app.models.channel import Channel
from .base_repository import BaseRepository
from app.interfaces.channel_interface import ChannelInterface

class ChannelRepository(BaseRepository, ChannelInterface):
    def get_channels(self) -> list[Channel]:
        query = "SELECT * FROM channel ORDER BY id ASC"
        db_result = self._execute(query)
        if not db_result.success:
            raise Exception(f"Failed getting channels from DB because {e}")

        try:
            return [Channel(**channel) for channel in db_result.data]
        except Exception as e:
            raise e
