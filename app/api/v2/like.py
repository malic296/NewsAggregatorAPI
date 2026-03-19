from fastapi import APIRouter, Depends, status
from app.dependencies.service_container import get_service_container
from app.dependencies.auth import get_current_user
from app.schemas import ResponseDTO
from app.models import Consumer

like_router = APIRouter(
    prefix="/likes",
    tags=["likes"]
    )

@like_router.post("/like_article", response_model=ResponseDTO)
def like_article(article_uuid: str, user: Consumer = Depends(get_current_user), services = Depends(get_service_container)):
    liked: bool = services.db.like_article(article_uuid, user)
    return ResponseDTO(
        success= True,
        message = f"Article with uuid {article_uuid} has been liked." if liked else f"Article with uuid {article_uuid} has been unliked.",
        status_code=status.HTTP_200_OK

    )