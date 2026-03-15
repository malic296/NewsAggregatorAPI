from dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class ChannelDTO(BaseModel):
    uuid: str
    title: str
    link: str
