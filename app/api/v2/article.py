from fastapi import Depends, APIRouter, Query
from app.repositories import ArticleRepository, ChannelRepository
from app.services import DatabaseService
from app.schemas import ArticleDTO

article_router = APIRouter()

def get_database_service() -> DatabaseService:
    return DatabaseService(
        article_repository=ArticleRepository(),
        channel_repository=ChannelRepository()
    )

@article_router.get("/articles", response_model=list[ArticleDTO])
def get_articles(
        hours: int = 1,
        channel_ids: list[int] = Query(default=None),
        db: DatabaseService = Depends(get_database_service)):
    return db.get_articles(hours=hours, channel_ids=channel_ids)
