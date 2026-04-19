from app.models import Channel
from app.schemas import ChannelDTO
from app.interfaces import ChannelInterface
from .cache_service import CacheService

class ChannelService:
    def __init__(self, channels: ChannelInterface, cache: CacheService):
        self.channels = channels
        self.cache = cache

    def get_channels(self, user_id: int) -> list[Channel]:
        cached_channels = self.cache.get_available_channels(user_id=user_id)
        if cached_channels:
            return cached_channels

        channels = self.channels.get_channels(user_id)
        self.cache.set_available_channels(channels=channels, user_id=user_id)
        return channels

    def set_disabled_channels(self, user_id: int, disabled_channels: list[ChannelDTO]) -> None:
        self.cache.invalidate_cache_channels(user_id=user_id)
        self.channels.set_disabled_channels_by_uuids(user_id, [channel.uuid for channel in disabled_channels])
