from .base_response import BaseResponse
from app.schemas import ChannelDTO

class ChannelsResponse(BaseResponse):
    channels: list[ChannelDTO]