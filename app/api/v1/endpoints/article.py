from fastapi import Depends, APIRouter
from app.models import Article, Consumer
from app.schemas.responses import ArticlesResponse, ArticleResponse, LikeResponse
from app.api.dependencies import get_article_service, get_current_user
from dataclasses import asdict
from app.schemas import ArticleDTO

article_router = APIRouter(
    prefix = "/articles",
    tags = ["articles"]
)

@article_router.get("/", response_model=ArticlesResponse)
def articles(hours: int = 1, user = Depends(get_current_user), article_service = Depends(get_article_service)):
    articles: list[Article] = article_service.get_articles(consumer=user, hours=hours)
    
    return ArticlesResponse(
        message="Articles fetched correctly",
        success=True,
        articles=[ArticleDTO(**asdict(article)) for article in articles]
    )

@article_router.get("/{uuid}", response_model=ArticleResponse)
def article(uuid: str, article_service = Depends(get_article_service)):
    article: Article = article_service.get_article(uuid)

    return ArticleResponse(
        message="Article fetched correctly",
        success=True,
        article=ArticleDTO(**asdict(article))
    )

@article_router.post("/{article_uuid}/like", response_model=LikeResponse)
def like(article_uuid: str, user: Consumer = Depends(get_current_user), article_service = Depends(get_article_service)):
    liked: bool = article_service.like_article(article_uuid, user)
    return LikeResponse(
        success= True,
        message = f"Article with uuid {article_uuid} has been liked." if liked else f"Article with uuid {article_uuid} has been unliked.",
        liked=liked
    )

