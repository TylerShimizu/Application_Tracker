from fastapi import APIRouter, Depends, HTTPException

from app.db.schema import SessionLocal
from app.models.user import UserCreate, UserRead
from app.services.user_service import UserService

router = APIRouter()

def get_user_service() -> UserService:
    return UserService(session=SessionLocal())

@router.get("/users", response_model=list[UserRead])
def get_users(service: UserService = Depends(get_user_service)):
    """Get a list of all users."""
    return service.list_user()

@router.post("/users", response_model=UserRead)
def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    """Create a new user."""
    return service.create_user(name=user.name)

@router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    """Get a user by ID."""
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, user: UserCreate, service: UserService = Depends(get_user_service)):
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