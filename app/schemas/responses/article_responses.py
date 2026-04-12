from .base_response import BaseResponse
from app.schemas import ArticleDTO
from typing import Optional

class ArticlesResponse(BaseResponse):
    articles: list[ArticleDTO]

class ArticleResponse(BaseResponse):
    article: Optional[ArticleDTO]