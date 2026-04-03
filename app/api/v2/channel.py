from fastapi import Depends, APIRouter, status
from app.dependencies.auth import get_current_user
from app.dependencies.service_container import get_service_container
from app.models import Channel, Consumer
from app.core.util import ServiceContainer
from app.schemas import ChannelDTO
from app.schemas.responses import ChannelsResponse, BaseResponse
from dataclasses import asdict

channel_router = APIRouter(
    prefix="/channels",
    tags=["channels"],
    dependencies=[Depends(get_current_user)]
)

@channel_router.get("/read_channels", response_model=ChannelsResponse)
def read_channels(services: ServiceContainer = Depends(get_service_container), user: Consumer = Depends(get_current_user)):
    channels: list[Channel] = services.cache.get_available_channels(user.id)
    if not channels:
        channels: list[Channel] = services.db.get_channels(user.id)
        services.cache.set_available_channels(channels, user.id)
        
    return ChannelsResponse(
        status_code=200,
        message="Channels fetched correctly",
        success=True,
        channels=[ChannelDTO(**asdict(channel)) for channel in channels]
    )

@channel_router.post("/set_disabled_channels", response_model=BaseResponse)
def set_disabled_channels(disabled_channels: list[ChannelDTO], user: Consumer = Depends(get_current_user), services: ServiceContainer = Depends(get_service_container)):
    services.cache.invalidate_cache_channels(user.id)
    services.db.set_disabled_channels(user.id, disabled_channels)
    return BaseResponse(
        success=True,
        message=f"Channels have been disabled for logged user.",
        status_code=status.HTTP_200_OK
    )