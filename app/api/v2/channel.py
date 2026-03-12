from fastapi import Depends, APIRouter
from app.repositories import ArticleRepository, ChannelRepository, ConsumerRepository
from app.services import DatabaseService
from app.schemas import ChannelDTO

channel_router = APIRouter()

def get_database_service() -> DatabaseService:
    return DatabaseService(
        article_repository=ArticleRepository(),
        channel_repository=ChannelRepository(),
        consumer_repository=ConsumerRepository()
    )

@channel_router.get("/channels", response_model=list[ChannelDTO])
def get_channels(db: DatabaseService = Depends(get_database_service)):
    return db.get_channels()