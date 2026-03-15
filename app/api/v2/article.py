from fastapi import Depends, APIRouter, Query
from app.models.service_container import ServiceContainer
from app.schemas import ArticleDTO
from app.dependencies.service_container import get_service_container
from app.dependencies.auth import get_current_user
from app.schemas import ResponseDTO

article_router = APIRouter(
    prefix = "/articles",
    tags = ["articles"],
    dependencies=[Depends(get_current_user)]
)

@article_router.get("/", response_model=ResponseDTO[list[ArticleDTO]])
def get_articles(hours: int = 1, channel_ids: list[int] = Query(default=None), services: ServiceContainer = Depends(get_service_container)):
    articles = services.db.get_articles(hours=hours, channel_ids=channel_ids)
    return ResponseDTO(
        status_code=200,
        message="Articles fetched correctly",
        success=True,
        data=articles
    )
