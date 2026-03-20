from fastapi import Depends, APIRouter
from app.dependencies.service_container import get_service_container
from app.dependencies.auth import get_current_user
from app.core.util import ServiceContainer
from app.schemas import ChannelDTO

channel_router_v1 = APIRouter()

@channel_router_v1.get("/channels", response_model=list[ChannelDTO])
def get_channels(services: ServiceContainer = Depends(get_service_container), user = Depends(get_current_user)):
    return services.db.get_channels()