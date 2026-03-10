from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserRead(BaseModel):
    id: int
    username: str

@app.get("/user/{user_id}", response_model=UserRead)
def get_user_endpoint(user_id: int):
    dummy_user = {"id": user_id, "username": "JohnDoe", "password": "SECRET_PASSWORD"}
    return dummy_user