from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db

from models.user_model import User

from schemas.notification_schema import (
    NotificationResponse
)

from services.notification_service import (
    NotificationService
)

from utils.dependencies import (
    get_current_user
)


router = APIRouter(
    prefix="/api/v1/notifications",
    tags=["Notifications"]
)


# =========================================================
# GET ALL NOTIFICATIONS
# =========================================================

@router.get(
    "/",
    response_model=list[NotificationResponse]
)
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return NotificationService.get_user_notifications(
        db=db,
        user_id=current_user.id
    )


# =========================================================
# GET UNREAD NOTIFICATIONS
# =========================================================

@router.get(
    "/unread",
    response_model=list[NotificationResponse]
)
def get_unread_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return NotificationService.get_unread_notifications(
        db=db,
        user_id=current_user.id
    )


# =========================================================
# MARK NOTIFICATION AS READ
# =========================================================

@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return NotificationService.mark_as_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )