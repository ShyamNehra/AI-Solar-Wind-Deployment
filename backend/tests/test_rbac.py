import pytest
from fastapi import HTTPException, status
from app.api.dependencies import RoleChecker
from app.models.user import User, Role

def test_rbac_admin_always_allowed():
    # Admin role should bypass all checks
    admin_role = Role(name="Administrator")
    user = User(email="admin@example.com", is_active=True)
    user.roles.append(admin_role)
    
    checker = RoleChecker(allowed_roles=["Planner", "GIS Analyst"])
    # Should not raise exception
    checked_user = checker(current_user=user)
    assert checked_user == user

def test_rbac_role_match_allowed():
    planner_role = Role(name="Planner")
    user = User(email="planner@example.com", is_active=True)
    user.roles.append(planner_role)
    
    checker = RoleChecker(allowed_roles=["Planner"])
    checked_user = checker(current_user=user)
    assert checked_user == user

def test_rbac_deny_by_default_raises_403():
    planner_role = Role(name="Planner")
    user = User(email="planner@example.com", is_active=True)
    user.roles.append(planner_role)
    
    # Allowed roles does not include Planner
    checker = RoleChecker(allowed_roles=["GIS Analyst", "Project Manager"])
    
    with pytest.raises(HTTPException) as exc_info:
        checker(current_user=user)
        
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "not have enough privileges" in exc_info.value.detail
