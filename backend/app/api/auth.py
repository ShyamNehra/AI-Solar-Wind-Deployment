from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.models.user import User, Role
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.user import UserCreate, UserOut, Token
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system."
        )
    
    # Retrieve role
    role = db.query(Role).filter(Role.name == user_in.role_name).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{user_in.role_name}' does not exist."
        )
    
    # Create user
    hashed_password = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        is_active=True
    )
    user.roles.append(role)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Format roles for response
    return UserOut(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        roles=[r.name for r in user.roles]
    )

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token = create_access_token(subject=user.email)
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active,
        roles=[r.name for r in current_user.roles]
    )

# stub for oauth2 login
@router.get("/oauth2")
def oauth2_stub():
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="OAuth2 external provider login is not implemented. Please use username/password login."
    )
