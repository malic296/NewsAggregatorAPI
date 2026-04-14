from fastapi import status
from typing import Optional

class InternalError(Exception):
    def __init__(self, *, public_message: Optional[str] = None, internal_message: Optional[str] = None, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(internal_message or public_message)

        self.public_message = public_message if public_message else "Request failed because of Internal Server Error"
        self.internal_message = internal_message if internal_message else None
        self.status_code = status_code
