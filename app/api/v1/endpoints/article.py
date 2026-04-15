from fastapi import Depends, APIRouter
from app.models import Article
from app.schemas.responses import ArticlesResponse, ArticleResponse
from app.api.dependencies import get_database_service, get_current_user
from dataclasses import asdict
from app.schemas import ArticleDTO
from typing import Optional

article_router = APIRouter(
    prefix = "/articles",
    tags = ["articles"]
)

@article_router.get("/read_articles", response_model=ArticlesResponse)
def read_articles(hours: int = 1, user = Depends(get_current_user), db = Depends(get_database_service)):
    articles: list[Article] = db.get_articles(consumer=user, hours=hours)
    
    return ArticlesResponse(
        status_code=200,
        message="Articles fetched correctly",
        success=True,
        articles=[ArticleDTO(**asdict(article)) for article in articles]
    )

@article_router.get("/read_article", response_model=ArticleResponse)
def read_article(uuid: str, db = Depends(get_database_service)):
    article: Optional[Article] = db.get_article(uuid)

    return ArticleResponse(
        status_code=200 if article else 404,
        message="Article fetched correctly" if article else "No article found for provided uuid.",
        success=True if article else False,
        article=ArticleDTO(**asdict(article)) if article else None
    )

