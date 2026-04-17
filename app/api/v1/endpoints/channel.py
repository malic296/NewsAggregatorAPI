from fastapi import Depends, APIRouter, status
from app.api.dependencies import get_current_user, get_channel_service
from app.models import Channel, Consumer
from app.schemas import ChannelDTO
from app.schemas.responses import ChannelsResponse, BaseResponse
from dataclasses import asdict

channel_router = APIRouter(
    prefix="/channels",
    tags=["channels"],
    dependencies=[Depends(get_current_user)]
)

@channel_router.get("/read_channels", response_model=ChannelsResponse)
def read_channels(channel_service = Depends(get_channel_service), user: Consumer = Depends(get_current_user)):
    channels: list[Channel] = channel_service.get_channels(user.id)
        
    return ChannelsResponse(
        message="Channels fetched correctly",
        success=True,
        channels=[ChannelDTO(**asdict(channel)) for channel in channels]
    )

@channel_router.post("/set_disabled_channels", response_model=BaseResponse)
def set_disabled_channels(disabled_channels: list[ChannelDTO], user: Consumer = Depends(get_current_user), channel_service = Depends(get_channel_service)):
    channel_service.set_disabled_channels(user.id, disabled_channels)

    return BaseResponse(
        success=True,
        message=f"Channels have been disabled for logged user."
    )