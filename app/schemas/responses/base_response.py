from pydantic import BaseModel

class BaseResponse(BaseModel):
    success: bool
    message: str
    status_code: int