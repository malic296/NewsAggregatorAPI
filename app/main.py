from fastapi import FastAPI
from app.api.v1.article import article_router
from app.api.v1.channel import channel_router

app = FastAPI()

app.include_router(article_router)
app.include_router(channel_router)