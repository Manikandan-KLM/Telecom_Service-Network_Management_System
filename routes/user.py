from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from repositories.user_repository import UserRepository
from schemas.user_schema import (
    AccountStatusRequest,
    ChangeRoleRequest,
    UserResponse,
)
from utils.dependencies import (
    get_current_user,
    require_roles,
)


router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"]
)


@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user=Depends(get_current_user)
):

    return current_user


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse
)
def change_role(
    user_id: int,
    request: ChangeRoleRequest,
    current_user=Depends(
        require_roles("Super Admin")
    ),
    db: Session = Depends(get_db)
):

    allowed_roles = {
        "Super Admin",
        "Operations Manager",
        "Support Agent",
        "Network Engineer",
        "Field Technician",
        "Customer"
    }

    if request.role not in allowed_roles:

        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    user = UserRepository.get_by_id(
        db,
        user_id
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.role = request.role

    return UserRepository.update(
        db,
        user
    )


@router.patch(
    "/{user_id}/status",
    response_model=UserResponse
)
def change_account_status(
    user_id: int,
    request: AccountStatusRequest,
    current_user=Depends(
        require_roles("Super Admin")
    ),
    db: Session = Depends(get_db)
):

    user = UserRepository.get_by_id(
        db,
        user_id
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.id == current_user.id:

        raise HTTPException(
            status_code=400,
            detail="You cannot deactivate your own account"
        )

    user.is_active = request.is_active

    return UserRepository.update(
        db,
        user
    )