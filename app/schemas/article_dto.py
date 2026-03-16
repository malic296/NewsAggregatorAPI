from datetime import datetime
from pydantic import BaseModel

class ArticleDTO(BaseModel):
    uuid: str
    title: str
    link: str
    description: str
    pub_date: datetime
    channel_link: str
    likes: int
    liked_by_user: bool = False
