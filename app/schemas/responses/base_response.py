from pydantic import BaseModel

class BaseResponse(BaseModel):
    success: bool
    message: str

class PaginatedResponse(BaseResponse):
    total_count: int
    page: int
    page_size: int
    has_more: bool