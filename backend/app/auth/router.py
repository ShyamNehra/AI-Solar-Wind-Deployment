from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.auth.models import User, UserRole
from app.auth.schemas import (
    UserRegisterSchema, UserLoginSchema, UserResponseSchema,
    TokenSchema, UserUpdateSchema, UserRoleUpdateSchema
)
from app.auth.security import hash_password, verify_password, create_access_token
from app.auth.dependencies import get_current_user, require_role
from app.core.rate_limiter import limiter

router = APIRouter(prefix="/auth", tags=["User Authentication & Role-Based Access"])


# ──────────────────────────────────────────────────────
# PUBLIC ENDPOINTS
# ──────────────────────────────────────────────────────

import re

@router.get("/check-workspace")
def check_workspace_availability(workspace_code: str, db: Session = Depends(get_db)):
    """
    Real-time endpoint to check whether a 4-digit Team Workspace Code is already registered or available for creation.
    """
    code = str(workspace_code).strip()
    if not re.match(r"^\d{4}$", code):
        return {
            "workspace_code": code,
            "exists": False,
            "available_for_creation": False,
            "message": "Team Code must be a 4-digit number (e.g. 4892)."
        }
    
    existing_user = db.query(User).filter(User.organization_id == code).first()
    if existing_user:
        return {
            "workspace_code": code,
            "exists": True,
            "available_for_creation": False,
            "message": f"Workspace code '{code}' is already taken."
        }
    
    return {
        "workspace_code": code,
        "exists": False,
        "available_for_creation": True,
        "message": f"Workspace code '{code}' is available for creation."
    }


@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def register_user(request: Request, payload: UserRegisterSchema, db: Session = Depends(get_db)):
    """Register a new user account with email, username, team workspace selection, and role."""
    if db.query(User).filter((User.email == payload.email) | (User.username == payload.username)).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists."
        )
    
    workspace_code = str(payload.organization_id or "1001").strip()
    if not re.match(r"^\d{4}$", workspace_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team Code must be a 4-digit number (e.g. 1001, 4892)."
        )
    
    mode = str(payload.workspace_mode or "create").lower()
    existing_user = db.query(User).filter(User.organization_id == workspace_code).first()
    
    if mode == "create":
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Workspace code '{workspace_code}' is already taken. Please choose a unique workspace code."
            )
    elif mode == "join":
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workspace code '{workspace_code}' was not found. Please verify the code with your team lead or select 'Create New Team Workspace'."
            )
    
    new_user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        organization=payload.organization or (existing_user.organization if existing_user else "New Energy Team"),
        organization_id=workspace_code,
        role=payload.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenSchema)
@limiter.limit("5/minute")
def login_user(request: Request, payload: UserLoginSchema, db: Session = Depends(get_db)):
    """Authenticate user with email/username and password. Returns JWT token."""
    user = db.query(User).filter(
        (User.email == payload.username_or_email) | (User.username == payload.username_or_email)
    ).first()
    
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )
    
    if payload.organization_id:
        req_code = str(payload.organization_id).strip().upper()
        if user.organization_id != req_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User '@{user.username}' belongs to workspace '{user.organization_id}', not '{req_code}'."
            )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated. Contact an administrator."
        )
    
    access_token = create_access_token(data={
        "sub": str(user.id), 
        "role": user.role.value,
        "organization_id": user.organization_id or "ORG-INFOSYS-001"
    })
    return TokenSchema(
        access_token=access_token,
        role=user.role,
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        organization=user.organization,
        organization_id=user.organization_id or "ORG-INFOSYS-001"
    )


# ──────────────────────────────────────────────────────
# AUTHENTICATED USER ENDPOINTS
# ──────────────────────────────────────────────────────

@router.get("/me", response_model=UserResponseSchema)
def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get the profile of the currently authenticated user."""
    return current_user


@router.put("/me", response_model=UserResponseSchema)
def update_user_profile(
    payload: UserUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the authenticated user's own profile (name, org, bio)."""
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.organization is not None:
        current_user.organization = payload.organization
    if payload.bio is not None:
        current_user.bio = payload.bio
    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url
    
    db.commit()
    db.refresh(current_user)
    return current_user


# ──────────────────────────────────────────────────────
# ADMIN-ONLY ENDPOINTS
# ──────────────────────────────────────────────────────

@router.get("/users", response_model=List[UserResponseSchema])
def list_all_users(
    current_user: User = Depends(require_role([UserRole.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    """List all registered users (Administrator only)."""
    return db.query(User).order_by(User.created_at.desc()).all()


@router.put("/users/{user_id}/role", response_model=UserResponseSchema)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdateSchema,
    current_user: User = Depends(require_role([UserRole.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    """Change a user's role (Administrator only)."""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change your own role.")
    
    target_user.role = payload.role
    db.commit()
    db.refresh(target_user)
    return target_user


@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_role([UserRole.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    """Deactivate a user account (Administrator only). Soft-delete."""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account.")
    
    target_user.is_active = not target_user.is_active
    db.commit()
    db.refresh(target_user)
    return {"detail": f"User '{target_user.username}' is now {'active' if target_user.is_active else 'deactivated'}."}