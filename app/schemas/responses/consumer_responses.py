from .base_response import BaseResponse
from app.schemas import ConsumerDTO

class ConsumersResponse(BaseResponse):
    consumers: list[ConsumerDTO]

class LikeResponse(BaseResponse):
    liked: bool