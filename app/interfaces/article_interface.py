from abc import ABC, abstractmethod
from typing import Optional
from app.models import Article, Consumer

class ArticleInterface(ABC):
    @abstractmethod
    def get_articles(self, consumer: Consumer, channel_ids: Optional[list[int]] = None, hours: int = 1) -> list[Article]:
        raise NotImplementedError("get_articles method not implemented in article repository.")
    
    @abstractmethod
    def get_article_by_uuid(self, article_uuid: str) -> Optional[int]:
        raise NotImplementedError("get_article_by_uuid method not implemented in article repository.")
