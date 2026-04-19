from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ScrapedArticle:
    title: str
    link: str
    description: str
    pub_date: datetime

@dataclass
class ScrapedChannel:
    title: str
    link: str
    articles: list[ScrapedArticle] = field(default_factory=list)