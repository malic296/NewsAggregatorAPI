from fastapi import FastAPI
from app.api.v1.article import article_router_v1
from app.api.v1.channel import channel_router_v1
from app.api.v2.article import article_router
from app.api.v2.channel import channel_router
from app.api.v2.consumer import consumer_router
from app.api.v2.like import like_router
from app.core.errors import InternalError
from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.dependencies.logging import get_logging_handler
from app.handlers import LoggingHandler

app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, err: Exception):
    logger: LoggingHandler = get_logging_handler()
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    if isinstance(err, InternalError):
        if err.internal_message:
            logger.handle(err.internal_message)

        status_code = err.status_code
        message = err.public_message

    else:
        message = f"API failed unexpectedly"
        logger.handle(message + f" because: {str(err)} for request: {request}")

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message
        }
    )

app.include_router(article_router, prefix="/latest")
app.include_router(channel_router, prefix="/latest")
app.include_router(consumer_router, prefix="/latest")
app.include_router(like_router, prefix="/latest")

app.include_router(article_router_v1, prefix="/v1", tags=["obsolete"])
app.include_router(channel_router_v1, prefix="/v1", tags=["obsolete"])
