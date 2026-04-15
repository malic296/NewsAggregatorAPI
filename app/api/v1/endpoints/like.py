from fastapi import APIRouter, Depends, status
from app.api.dependencies import get_database_service, get_current_user
from app.schemas.responses import LikeResponse
from app.models import Consumer

like_router = APIRouter(
    prefix="/likes",
    tags=["likes"]
    )

@like_router.post("/like_article", response_model=LikeResponse)
def like_article(article_uuid: str, user: Consumer = Depends(get_current_user), db = Depends(get_database_service)):
    liked: bool = db.like_article(article_uuid, user)
    return LikeResponse(
        success= True,
        message = f"Article with uuid {article_uuid} has been liked." if liked else f"Article with uuid {article_uuid} has been unliked.",
        status_code=status.HTTP_200_OK,
        liked=liked
    )