import re

from pydantic import BaseModel, ConfigDict, field_validator

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 30
MIN_PASSWORD_LENGTH = 8


def validate_username(name: str) -> str:
    name = name.strip()

    if not name:
        raise ValueError("Username cannot be empty")
    if len(name) < MIN_USERNAME_LENGTH:
        raise ValueError(f"Username must be at least {MIN_USERNAME_LENGTH} characters")
    if len(name) > MAX_USERNAME_LENGTH:
        raise ValueError(f"Username cannot be longer than {MAX_USERNAME_LENGTH} characters")
    if not USERNAME_PATTERN.fullmatch(name):
        raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")

    return name


def validate_password(password: str) -> str:
    if not password or not password.strip():
        raise ValueError("Password cannot be empty")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters")

    return password

class UserCreate(BaseModel):
    name: str
    password: str

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, name: str) -> str:
        return validate_username(name)

    @field_validator("password")
    @classmethod
    def password_must_be_valid(cls, password: str) -> str:
        return validate_password(password)

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str

class UserUpdate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, name: str) -> str:
        return validate_username(name)

class UserLogin(BaseModel):
    name: str
    password: str

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, name: str) -> str:
        return validate_username(name)

    @field_validator("password")
    @classmethod
    def password_must_be_valid(cls, password: str) -> str:
        return validate_password(password)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
