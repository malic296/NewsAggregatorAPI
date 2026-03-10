from dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class ChannelDTO(BaseModel):
    id: int
    title: str
    link: str
