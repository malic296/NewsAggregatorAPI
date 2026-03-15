from fastapi import Depends, APIRouter
from app.models.service_container import ServiceContainer
from app.schemas import ChannelDTO
from app.dependencies.auth import get_current_user
from app.dependencies.service_container import get_service_container
from app.schemas import ResponseDTO

channel_router = APIRouter(
    prefix="/channels",
    tags=["channels"],
    dependencies=[Depends(get_current_user)]
)

@channel_router.get("/", response_model=ResponseDTO[list[ChannelDTO]])
def get_available_channels(services: ServiceContainer = Depends(get_service_container)):
    channels = services.db.get_channels()
    return ResponseDTO(
        status_code=200,
        message="Channels fetched correctly",
        success=True,
        data=channels
    )