from fastapi import Depends, APIRouter
from app.api.dependencies import get_current_user, get_channel_service
from app.models import Channel, Consumer
from app.schemas import ChannelDTO
from app.schemas.responses import ChannelsResponse, BaseResponse
from dataclasses import asdict

channel_router = APIRouter(
    prefix="/channels",
    tags=["channels"]
)

@channel_router.get("/", response_model=ChannelsResponse)
def channels(channel_service = Depends(get_channel_service), user: Consumer = Depends(get_current_user)):
    channels: list[Channel] = channel_service.get_channels(user.id)
        
    return ChannelsResponse(
        message="Channels fetched correctly",
        success=True,
        channels=[ChannelDTO(**asdict(channel)) for channel in channels]
    )

@channel_router.post("/disabled", response_model=BaseResponse)
def disabled(channels_to_disable: list[ChannelDTO], user: Consumer = Depends(get_current_user), channel_service = Depends(get_channel_service)):
    channel_service.set_disabled_channels(user.id, channels_to_disable)

    return BaseResponse(
        success=True,
        message=f"Channels have been disabled for logged user."
    )