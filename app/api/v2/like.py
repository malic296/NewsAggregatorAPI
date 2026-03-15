from fastapi import APIRouter, Depends, HTTPException
from app.dependencies.service_container import get_service_container

like_router = APIRouter(
    prefix="/likes",
    tags=["likes"]
    #dependencies for auth
    )

@like_router.post("/like_article")
def like_article(article_uuid: int, user_uuid: int, services = Depends(get_service_container)):
    try:
        return services.db.like_article(article_uuid, user_uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Liking article failed due to: {e}")