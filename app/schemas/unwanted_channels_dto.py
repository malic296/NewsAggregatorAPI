from pydantic import BaseModel

class UnwantedChannelsDTO(BaseModel):
    unwanted_channels: list[int]