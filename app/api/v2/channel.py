from fastapi import Depends, APIRouter
from app.models.service_container import ServiceContainer
from app.schemas import ChannelDTO
from app.dependencies.auth import get_current_user
from app.dependencies.service_container import get_service_container

channel_router = APIRouter(
    prefix="/channels",
    tags=["channels"],
    dependencies=[Depends(get_current_user)]
)

@channel_router.get("/", response_model=list[ChannelDTO])
def get_channels(services: ServiceContainer = Depends(get_service_container)):
    return services.db.get_channels()