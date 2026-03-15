from pydantic import BaseModel

class ConsumerDTO(BaseModel):
    uuid: str
    username: str
    email: str