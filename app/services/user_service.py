from sqlalchemy.orm import Session

from app.db.schema import User
from app.core.security import hash_password, verify_password

class UserService:
    """Service for managing users."""

    def __init__(self, session: Session):
        self._db = session

    def list_user(self) -> list[User]:
        return self._db.query(User).all()

    def create_user(self, name: str, password: str) -> User | None:
        """Create a new user."""
        existing_user = self.get_user_by_name(name=name)
        if existing_user:
            return None

        user = User(name=name, hashed_password=hash_password(password))
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    def get_user(self, user_id: int) -> User:
        """Get a user by ID."""
        return self._db.query(User).filter(User.id == user_id).first()

    def get_user_by_name(self, name: str) -> User | None:
        """Get a user by name."""
        return self._db.query(User).filter(User.name == name).first()

    def authenticate_user(self, name: str, password: str) -> User | None:
        """Return the user if the supplied login credentials are valid."""
        user = self.get_user_by_name(name=name)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def update_user(self, user_id: int, name: str) -> User | None:
        """Update a user's name."""
        user = self._db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        user.name = name
        self._db.commit()
        self._db.refresh(user)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user by ID."""
        user = self._db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        self._db.delete(user)
        self._db.commit()
        return True
