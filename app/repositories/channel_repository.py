from app.models.channel import Channel
from .base_repository import BaseRepository
from app.interfaces.channel_interface import ChannelInterface

class ChannelRepository(BaseRepository, ChannelInterface):
    def get_channels(self) -> list[Channel]:
        query = "SELECT * FROM channel ORDER BY id ASC"
        db_result = self._execute(query)

        try:
            channels: list[Channel] = [Channel(**channel) for channel in db_result]
        except Exception as e:
            raise e

        return channels