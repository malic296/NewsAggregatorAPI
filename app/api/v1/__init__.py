from fastapi import APIRouter
from .endpoints import article_router, channel_router, consumer_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(article_router)
v1_router.include_router(channel_router)
v1_router.include_router(consumer_router)