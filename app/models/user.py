from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    name: str
    password: str

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str

class UserUpdate(BaseModel):
    name: str

class UserLogin(BaseModel):
    name: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
