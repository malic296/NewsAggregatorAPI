from abc import ABC, abstractmethod
from app.models import Channel

class ChannelInterface(ABC):
    @abstractmethod
    def get_channels(self) -> list[Channel]:
        raise NotImplementedError("get_channels method not implemented in channel repository.")