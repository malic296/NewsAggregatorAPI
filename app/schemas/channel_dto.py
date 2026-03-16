from pydantic import BaseModel

class ChannelDTO(BaseModel):
    uuid: str
    title: str
    link: str
