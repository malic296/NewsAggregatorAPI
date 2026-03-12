from pydantic import BaseModel

class RegistrationDTO(BaseModel):
    username: str
    email: str
    password: str