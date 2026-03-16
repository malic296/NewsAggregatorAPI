from dataclasses import dataclass
from datetime import datetime

@dataclass
class Article:
    id: int
    uuid: str
    title: str
    link: str
    description: str
    pub_date: datetime
    channel_link: str
    likes: int
    liked_by_user: bool = False