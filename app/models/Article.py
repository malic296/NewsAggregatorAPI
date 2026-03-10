from dataclasses import dataclass
from datetime import datetime

@dataclass
class Article:
    id: int
    title: str
    link: str
    description: str
    pub_date: datetime
    channel_id: int