from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel

@dataclass
class ArticleDTO(BaseModel):
    id: int
    title: str
    link: str
    description: str
    pub_date: datetime
    channel_id: int
