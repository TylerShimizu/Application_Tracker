from sqlalchemy.orm import Session

from app.db.schema import User

class UserService:
    """Service for managing users."""

    def __init__(self, session: Session):
        self._db = session

    def list_user(self) -> list[User]:
        return self._db.query(User).all()

    def create_user(self, name: str) -> User:
        """Create a new user."""
        user = User(name=name)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user(self, user_id: int) -> User:
        """Get a user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def update_user(self, user_id: int, name: str) -> User | None:
        """Update a user's name."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        user.name = name
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user by ID."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True
