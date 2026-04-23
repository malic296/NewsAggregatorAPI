from .base_response import BaseResponse
from app.schemas import ConsumerDTO

class ConsumerResponse(BaseResponse):
    consumer: ConsumerDTO

class LikeResponse(BaseResponse):
    liked: bool