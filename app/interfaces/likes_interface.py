from abc import ABC, abstractmethod

class LikesInterface(ABC):
    @abstractmethod
    def like_article(self, article_id: int, consumer_id: int) -> bool:
        pass