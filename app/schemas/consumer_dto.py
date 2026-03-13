from pydantic import BaseModel

class ConsumerDTO(BaseModel):
    id: int
    username: str
    email: str