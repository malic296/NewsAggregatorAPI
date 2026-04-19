from .base_response import BaseResponse
from app.schemas import ConsumerDTO

class ConsumerResponse(BaseResponse):
    consumers: ConsumerDTO

class LikeResponse(BaseResponse):
    liked: bool