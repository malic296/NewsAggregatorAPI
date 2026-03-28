from abc import ABC, abstractmethod
from typing import Optional
from app.models import Article, Consumer

class ArticleInterface(ABC):
    @abstractmethod
    def get_articles(self, consumer: Consumer, hours: int = 1) -> list[Article]:
        ...
    
    @abstractmethod
    def article_uuid_to_id(self, article_uuid: str) -> Optional[int]:
        ...
