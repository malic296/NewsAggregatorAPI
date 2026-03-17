from fastapi import FastAPI
from app.api.v1.article import article_router_v1
from app.api.v1.channel import channel_router_v1
from app.api.v2.article import article_router
from app.api.v2.channel import channel_router
from app.api.v2.consumer import consumer_router
from app.api.v2.like import like_router
from app.models import BaseError
from fastapi import Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(BaseError)
async def custom_app_exception_handler(request: Request, err: BaseError):
    print(f"LOGGING: {err.internal_message}") 

    return JSONResponse(
        status_code=err.status_code,
        content={
            "success": False,
            "message": err.public_message,
            "data": None
        }
    )

app.include_router(article_router, prefix="/latest")
app.include_router(channel_router, prefix="/latest")
app.include_router(consumer_router, prefix="/latest")
app.include_router(like_router, prefix="/latest")

app.include_router(article_router_v1, prefix="/v1", tags=["obsolete"])
app.include_router(channel_router_v1, prefix="/v1", tags=["obsolete"])
