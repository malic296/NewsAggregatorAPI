from typing import Optional
from pydantic import BaseModel, model_validator

class LoginDTO(BaseModel):
    password: str
    username: Optional[str]
    email: Optional[str]

    @model_validator(mode="after")
    def validate_log_req(self) -> LoginDTO:
        if not self.username and not self.email:
            raise ValueError("Either username or email must be provided for login request")
        return self