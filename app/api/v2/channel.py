from fastapi import Depends, APIRouter, status
from app.dependencies.auth import get_current_user
from app.dependencies.service_container import get_service_container
from app.models import Channel, Consumer
from app.core.util import ServiceContainer
from app.schemas import ResponseDTO, ChannelDTO, UnwantedChannelsDTO

channel_router = APIRouter(
    prefix="/channels",
    tags=["channels"],
    dependencies=[Depends(get_current_user)]
)

@channel_router.get("/", response_model=ResponseDTO[list[ChannelDTO]])
def get_available_channels(services: ServiceContainer = Depends(get_service_container), user: Consumer = Depends(get_current_user)):
    channels: list[Channel] = services.cache.get_available_channels()
    if not channels:
        channels: list[Channel] = services.db.get_channels(user.id)
        services.cache.set_available_channels(channels)
        
    return ResponseDTO(
        status_code=200,
        message="Channels fetched correctly",
        success=True,
        data=channels
    )

@channel_router.post("/set_unwanted_channels", response_model=ResponseDTO[None])
def set_disabled_channels(channel_uuids: UnwantedChannelsDTO, user: Consumer = Depends(get_current_user), services: ServiceContainer = Depends(get_service_container)):
    services.db.set_disabled_channels(user.id, channel_uuids.unwanted_channels)
    return ResponseDTO(
        success=True,
        message=f"Channels have been disabled for logged user.",
        status_code=status.HTTP_200_OK
    )