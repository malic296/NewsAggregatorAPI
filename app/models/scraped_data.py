from dataclasses import dataclass
from .article import Article
from .channel import Channel

@dataclass
class ScrapedChannel:
    title: str
    link: str
    uuid: str
    articles: list[Article]