from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.core.security import oauth2_scheme, decode_access_token
from app.models.user import User

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = decode_access_token(token)
    if email is None:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        user_role_names = [role.name for role in current_user.roles]
        # Administrator role has superuser access, always allowed
        if "Administrator" in user_role_names:
            return current_user
        
        # Check if user has any of the allowed roles
        if not any(role in user_role_names for role in self.allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user does not have enough privileges to perform this action"
            )
        return current_user

# Convenience dependencies
def require_role(role_name: str):
    return RoleChecker([role_name])

def require_any_role(role_names: list[str]):
    return RoleChecker(role_names)

