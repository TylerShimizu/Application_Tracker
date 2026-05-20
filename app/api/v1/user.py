from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.security import create_access_token
from app.db.schema import User
from app.models.user import Token, UserCreate, UserLogin, UserRead, UserUpdate
from app.services.user_service import UserService

router = APIRouter()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(session=db)

@router.get("/users", response_model=list[UserRead])
def get_users(service: UserService = Depends(get_user_service)):
    """Get a list of all users."""
    return service.list_user()

@router.post("/users", response_model=UserRead)
def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    """Create a new user."""
    created_user = service.create_user(name=user.name, password=user.password)
    if not created_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return created_user

@router.post("/login", response_model=Token)
def login(user: UserLogin, service: UserService = Depends(get_user_service)):
    """Log in and receive a bearer token."""
    authenticated_user = service.authenticate_user(
        name=user.name,
        password=user.password,
    )
    if not authenticated_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return Token(access_token=create_access_token(user_id=authenticated_user.id))

@router.get("/users/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently logged-in user."""
    return current_user

@router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    """Get a user by ID."""
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, user: UserUpdate, service: UserService = Depends(get_user_service)):
    """Update a user's name."""
    updated_user = service.update_user(user_id, name=user.name)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, service: UserService = Depends(get_user_service)):
    """Delete a user by ID."""
    success = service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}
