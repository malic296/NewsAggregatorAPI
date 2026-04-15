from fastapi import Depends, APIRouter, status
from app.api.dependencies import get_current_user, get_database_service
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
def read_channels(db = Depends(get_database_service), user: Consumer = Depends(get_current_user)):
    channels: list[Channel] = db.get_channels(user.id)
        
    return ChannelsResponse(
        status_code=200,
        message="Channels fetched correctly",
        success=True,
        channels=[ChannelDTO(**asdict(channel)) for channel in channels]
    )

@channel_router.post("/set_disabled_channels", response_model=BaseResponse)
def set_disabled_channels(disabled_channels: list[ChannelDTO], user: Consumer = Depends(get_current_user), db = Depends(get_database_service)):
    db.set_disabled_channels(user.id, disabled_channels)

    return BaseResponse(
        success=True,
        message=f"Channels have been disabled for logged user.",
        status_code=status.HTTP_200_OK
    )