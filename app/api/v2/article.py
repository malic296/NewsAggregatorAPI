from fastapi import Depends, APIRouter, Query
from app.models import Article
from app.core.util import ServiceContainer
from app.schemas import ArticleDTO, ResponseDTO
from app.dependencies.service_container import get_service_container
from app.dependencies.auth import get_current_user

article_router = APIRouter(
    prefix = "/articles",
    tags = ["articles"]
)

@article_router.get("/", response_model=ResponseDTO[list[ArticleDTO]])
def get_articles(hours: int = 1, user = Depends(get_current_user), services: ServiceContainer = Depends(get_service_container)):
    articles: list[Article] = services.db.get_articles(consumer=user, hours=hours)
    
    return ResponseDTO(
        status_code=200,
        message="Articles fetched correctly",
        success=True,
        data=articles
    )
