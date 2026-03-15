from pydantic import BaseModel
from typing import TypeVar, Generic, Optional

T = TypeVar("T")

class ResponseDTO(BaseModel, Generic[T]):
    success: bool
    message: str
    status_code: int
    data: Optional[T] = None