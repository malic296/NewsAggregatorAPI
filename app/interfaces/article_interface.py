from abc import ABC, abstractmethod
from app.models import Article

class ArticleInterface(ABC):
    @abstractmethod
    def get_articles(self) -> list[Article]:
        pass

    @abstractmethod
    def get_articles_by_channels(self, channel_ids: list[int]) -> list[Article]:
        pass