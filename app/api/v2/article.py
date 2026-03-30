from fastapi import Depends, APIRouter, Query
from app.models import Article
from app.core.util import ServiceContainer
from app.schemas.responses import ArticlesResponse
from app.dependencies.service_container import get_service_container
from app.dependencies.auth import get_current_user
from dataclasses import asdict
from app.schemas import ArticleDTO

article_router = APIRouter(
    prefix = "/articles",
    tags = ["articles"]
)

@article_router.get("/read_articles", response_model=ArticlesResponse)
def read_articles(hours: int = 1, user = Depends(get_current_user), services: ServiceContainer = Depends(get_service_container)):
    articles: list[Article] = services.db.get_articles(consumer=user, hours=hours)
    
    return ArticlesResponse(
        status_code=200,
        message="Articles fetched correctly",
        success=True,
        articles=[ArticleDTO(**asdict(article)) for article in articles]
    )
