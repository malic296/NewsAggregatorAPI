from fastapi import Depends, APIRouter
from app.dependencies.service_container import get_service_container
from app.dependencies.auth import get_current_user
from app.core.util import ServiceContainer
from app.schemas import ArticleDTO

article_router_v1 = APIRouter()

@article_router_v1.get("/articles", response_model=list[ArticleDTO])
def get_articles(services: ServiceContainer = Depends(get_service_container), user = Depends(get_current_user)):
    return services.db.get_articles(consumer=user)