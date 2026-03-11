from fastapi import FastAPI
from app.api.v1.article import article_router_v1
from app.api.v1.channel import channel_router_v1

from app.api.v2.article import article_router
from app.api.v2.channel import channel_router

app = FastAPI()

app.include_router(article_router_v1, prefix="/v1")
app.include_router(channel_router_v1, prefix="/v1")

app.include_router(article_router, prefix="/latest")
app.include_router(channel_router, prefix="/latest")