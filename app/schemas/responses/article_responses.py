from .base_response import BaseResponse
from app.schemas import ArticleDTO

class ArticlesResponse(BaseResponse):
    articles: list[ArticleDTO]