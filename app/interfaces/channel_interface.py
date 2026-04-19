from abc import ABC, abstractmethod
from app.models import Channel
from app.models.scraped_data import ScrapedChannel


class ChannelInterface(ABC):
    @abstractmethod
    def get_channels(self, user_id: int) -> list[Channel]:
        ...

    @abstractmethod
    def set_disabled_channels_by_uuids(self, user_id: int, channel_ids: list[str]) -> None:
        ...

    @abstractmethod
    def update_channels(self, channels: list[ScrapedChannel]) -> None:
        ...