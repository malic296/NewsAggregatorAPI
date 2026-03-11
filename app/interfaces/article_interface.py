from abc import ABC, abstractmethod
from typing import Optional
from app.models import Article

class ArticleInterface(ABC):
    @abstractmethod
    def get_articles(self, channel_ids: Optional[list[int]] = None, hours: int = 1) -> list[Article]:
        raise NotImplementedError("get_articles method not implemented")
