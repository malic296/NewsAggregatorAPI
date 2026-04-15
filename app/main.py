from fastapi import FastAPI, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import v1_router
from app.core.errors import InternalError
from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.api.dependencies import get_logging_handler
from app.handlers import LoggingHandler
from app.schemas.responses import BaseResponse
from app.api.dependencies import generate_unique_endpoint_id

#USE FOR TESTS
#app = FastAPI(generate_unique_id_function=generate_unique_endpoint_id)

#USE FOR PRODUCTION
app = FastAPI(generate_unique_id_function=generate_unique_endpoint_id)

def create_error_response(message: str, status_code: int) -> JSONResponse:
    response: BaseResponse = BaseResponse(
        success=False,
        message=message,
        status_code=status_code
    )

    return JSONResponse(
        status_code=status_code,
        content=response.model_dump()
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, err: Exception):
    logger: LoggingHandler = get_logging_handler()

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "API failed unexpectedly"

    if isinstance(err, InternalError):
        if err.internal_message:
            logger.handle(err.internal_message)

        status_code = err.status_code
        message = err.public_message

    else:
        logger.handle(f"Unexpected Error: {str(err)} | Path: {request.url.path}")

    return create_error_response(message = message, status_code = status_code)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, err: HTTPException):
    message = err.detail if err.detail else 'Unexpected HTTP error'
    if err.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        message = "You have exceeded the rate limit."

    return create_error_response(message = message, status_code = err.status_code)

@app.middleware("http")
async def log_request(request: Request, call_next):
    response = await call_next(request)

    try:
        handler: LoggingHandler = get_logging_handler()
        log = f"IP: {request.client.host if request.client else 'Unknown'} | {request.method} {request.url.path} | Status: {response.status_code}"

        handler.handle(log)
    except Exception as err:
        print(f"CRITICAL: Could not save log because: {str(err)}")

    return response

#app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"]
)
app.include_router(v1_router)
