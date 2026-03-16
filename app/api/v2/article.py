from fastapi import Depends, APIRouter, Query
from app.models.service_container import ServiceContainer
from app.schemas import ArticleDTO
from app.dependencies.service_container import get_service_container
from app.dependencies.auth import get_current_user
from app.schemas import ResponseDTO
from app.models.article import Article

article_router = APIRouter(
    prefix = "/articles",
    tags = ["articles"]
)

@article_router.get("/", response_model=ResponseDTO[list[ArticleDTO]])
def get_articles(hours: int = 1, channel_ids: list[int] = Query(default=None), user = Depends(get_current_user), services: ServiceContainer = Depends(get_service_container)):
    consumer = services.db.get_consumer_by_credential(user["username"])
    if not consumer:
        raise Exception("Logged user not found")
    
    articles: list[Article] = services.db.get_articles(consumer=consumer, hours=hours, channel_ids=channel_ids)
    
    return ResponseDTO(
        status_code=200,
        message="Articles fetched correctly",
        success=True,
        data=articles
    )
