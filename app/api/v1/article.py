from fastapi import Depends, APIRouter
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
def get_articles(db: DatabaseService = Depends(get_database_service)):
    return db.get_articles()

@article_router.get("/articles/{channel_id}", response_model=list[ArticleDTO])
def get_articles_by_channel_ids(channel_id: int, db: DatabaseService = Depends(get_database_service)):
    return db.get_articles_by_channels([channel_id])