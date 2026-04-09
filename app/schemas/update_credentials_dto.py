from typing import Optional
from pydantic import BaseModel

class UpdateCredentialsDTO(BaseModel):
    old_password: str
    new_password: Optional[str] = None
    new_username: Optional[str] = None