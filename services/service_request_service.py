import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.service_request_model import ServiceRequest
from models.service_request_history_model import ServiceRequestHistory
from models.customer_model import Customer
from models.user_model import User

from repositories.service_request_repository import (
    ServiceRequestRepository
)

from repositories.service_request_history_repository import (
    ServiceRequestHistoryRepository
)


class ServiceRequestService:

    # =========================================================
    # ALLOWED VALUES
    # =========================================================

    REQUEST_TYPES = {
        "SIM Replacement",
        "Number Change",
        "Plan Change",
        "Device Replacement",
        "Service Activation",
        "Service Suspension",
        "Service Termination"
    }

    STATUSES = {
        "Submitted",
        "Under Review",
        "Approved",
        "Rejected",
        "In Progress",
        "Completed",
        "Cancelled"
    }

    PRIORITIES = {
        "Low",
        "Medium",
        "High",
        "Critical"
    }

    # =========================================================
    # STATUS TRANSITIONS
    # =========================================================

    ALLOWED_TRANSITIONS = {
        "Submitted": {
            "Under Review",
            "Cancelled"
        },

        "Under Review": {
            "Approved",
            "Rejected",
            "Cancelled"
        },

        "Approved": {
            "In Progress",
            "Cancelled"
        },

        "In Progress": {
            "Completed",
            "Cancelled"
        },

        "Rejected": set(),

        "Completed": set(),

        "Cancelled": set()
    }

    # =========================================================
    # REQUEST NUMBER
    # =========================================================

    @staticmethod
    def generate_request_number() -> str:
        """
        Generate unique service request number.

        Example:
        SR-7A91F2C3
        """

        unique_part = uuid.uuid4().hex[:8].upper()

        return f"SR-{unique_part}"

    # =========================================================
    # VALIDATE REQUEST TYPE
    # =========================================================

    @staticmethod
    def validate_request_type(request_type: str):

        if request_type not in ServiceRequestService.REQUEST_TYPES:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid request type. "
                    f"Allowed values: "
                    f"{', '.join(ServiceRequestService.REQUEST_TYPES)}"
                )
            )

    # =========================================================
    # VALIDATE PRIORITY
    # =========================================================

    @staticmethod
    def validate_priority(priority: str):

        if priority not in ServiceRequestService.PRIORITIES:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid priority. "
                    f"Allowed values: "
                    f"{', '.join(ServiceRequestService.PRIORITIES)}"
                )
            )

    # =========================================================
    # VALIDATE STATUS
    # =========================================================

    @staticmethod
    def validate_status(status: str):

        if status not in ServiceRequestService.STATUSES:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid status. "
                    f"Allowed values: "
                    f"{', '.join(ServiceRequestService.STATUSES)}"
                )
            )

    # =========================================================
    # ADD HISTORY
    # =========================================================

    @staticmethod
    def add_history(
        db: Session,
        request_id: int,
        changed_by: int,
        old_status: str | None,
        new_status: str,
        remarks: str | None = None
    ):

        history = ServiceRequestHistory(
            service_request_id=request_id,
            changed_by=changed_by,
            old_status=old_status,
            new_status=new_status,
            remarks=remarks
        )

        return ServiceRequestHistoryRepository.create(
            db,
            history
        )

    # =========================================================
    # CREATE SERVICE REQUEST
    # =========================================================

    @staticmethod
    def create_request(
        db: Session,
        customer_id: int,
        request_type: str,
        description: str,
        priority: str = "Medium",
        sim_id: int | None = None,
        subscription_id: int | None = None,
        device_id: int | None = None
    ):

        # -----------------------------------------
        # Validate request type
        # -----------------------------------------

        ServiceRequestService.validate_request_type(
            request_type
        )

        # -----------------------------------------
        # Validate priority
        # -----------------------------------------

        ServiceRequestService.validate_priority(
            priority
        )

        # -----------------------------------------
        # Find customer
        # -----------------------------------------

        customer = (
            db.query(Customer)
            .filter(
                Customer.id == customer_id
            )
            .first()
        )

        if not customer:

            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        # -----------------------------------------
        # Customer must be active
        # -----------------------------------------

        if not customer.is_active:

            raise HTTPException(
                status_code=400,
                detail="Inactive customer cannot create service request"
            )

        # -----------------------------------------
        # Request number
        # -----------------------------------------

        request_number = (
            ServiceRequestService.generate_request_number()
        )

        # -----------------------------------------
        # Create request
        # -----------------------------------------

        service_request = ServiceRequest(
            request_number=request_number,
            customer_id=customer_id,
            sim_id=sim_id,
            subscription_id=subscription_id,
            device_id=device_id,
            request_type=request_type,
            description=description,
            status="Submitted",
            priority=priority
        )

        service_request = ServiceRequestRepository.create(
            db,
            service_request
        )

        # -----------------------------------------
        # Initial history
        # -----------------------------------------

        ServiceRequestService.add_history(
            db=db,
            request_id=service_request.id,
            changed_by=customer.user_id,
            old_status=None,
            new_status="Submitted",
            remarks="Service request created"
        )

        return service_request

    # =========================================================
    # ASSIGN SERVICE REQUEST
    # =========================================================

    @staticmethod
    def assign_request(
        db: Session,
        request_id: int,
        assigned_to: int,
        changed_by: int
    ):

        # -----------------------------------------
        # Get request
        # -----------------------------------------

        service_request = (
            ServiceRequestRepository.get_by_id(
                db,
                request_id
            )
        )

        if not service_request:

            raise HTTPException(
                status_code=404,
                detail="Service request not found"
            )

        # -----------------------------------------
        # Cannot assign completed/rejected/cancelled
        # -----------------------------------------

        if service_request.status in {
            "Completed",
            "Rejected",
            "Cancelled"
        }:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Cannot assign request with "
                    f"status '{service_request.status}'"
                )
            )

        # -----------------------------------------
        # Find assigned user
        # -----------------------------------------

        user = (
            db.query(User)
            .filter(
                User.id == assigned_to
            )
            .first()
        )

        if not user:

            raise HTTPException(
                status_code=404,
                detail="Assigned user not found"
            )

        # -----------------------------------------
        # User must be active
        # -----------------------------------------

        if not user.is_active:

            raise HTTPException(
                status_code=400,
                detail="Cannot assign request to inactive user"
            )

        old_status = service_request.status

        # -----------------------------------------
        # Assign
        # -----------------------------------------

        service_request.assigned_to = assigned_to

        # -----------------------------------------
        # Submitted -> Under Review
        # -----------------------------------------

        if service_request.status == "Submitted":

            service_request.status = "Under Review"

        # -----------------------------------------
        # Approved -> In Progress
        # -----------------------------------------

        elif service_request.status == "Approved":

            service_request.status = "In Progress"

        service_request = ServiceRequestRepository.update(
            db,
            service_request
        )

        # -----------------------------------------
        # History
        # -----------------------------------------

        if old_status != service_request.status:

            remarks = (
                f"Request assigned to user {assigned_to}"
            )

            ServiceRequestService.add_history(
                db=db,
                request_id=request_id,
                changed_by=changed_by,
                old_status=old_status,
                new_status=service_request.status,
                remarks=remarks
            )

        else:

            ServiceRequestService.add_history(
                db=db,
                request_id=request_id,
                changed_by=changed_by,
                old_status=old_status,
                new_status=old_status,
                remarks=(
                    f"Request assigned to user "
                    f"{assigned_to}"
                )
            )

        return service_request

    # =========================================================
    # UPDATE STATUS
    # =========================================================

    @staticmethod
    def update_status(
        db: Session,
        request_id: int,
        new_status: str,
        changed_by: int,
        remarks: str | None = None,
        rejection_reason: str | None = None,
        completion_notes: str | None = None
    ):

        # -----------------------------------------
        # Validate status
        # -----------------------------------------

        ServiceRequestService.validate_status(
            new_status
        )

        # -----------------------------------------
        # Get request
        # -----------------------------------------

        service_request = (
            ServiceRequestRepository.get_by_id(
                db,
                request_id
            )
        )

        if not service_request:

            raise HTTPException(
                status_code=404,
                detail="Service request not found"
            )

        old_status = service_request.status

        # -----------------------------------------
        # Same status is not allowed
        # -----------------------------------------

        if old_status == new_status:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Request is already in "
                    f"'{new_status}' status"
                )
            )

        # -----------------------------------------
        # Validate transition
        # -----------------------------------------

        allowed_next_statuses = (
            ServiceRequestService.ALLOWED_TRANSITIONS
            .get(old_status, set())
        )

        if new_status not in allowed_next_statuses:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid status transition: "
                    f"{old_status} -> {new_status}"
                )
            )

        # =====================================================
        # REJECTED
        # =====================================================

        if new_status == "Rejected":

            if not rejection_reason:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Rejection reason is required "
                        "when rejecting a request"
                    )
                )

            service_request.rejection_reason = (
                rejection_reason
            )

        # =====================================================
        # COMPLETED
        # =====================================================

        if new_status == "Completed":

            if not completion_notes:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Completion notes are required "
                        "when completing a request"
                    )
                )

            # -----------------------------------------
            # Assignment required
            # -----------------------------------------

            if not service_request.assigned_to:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Service request must be assigned "
                        "before completion"
                    )
                )

            service_request.completion_notes = (
                completion_notes
            )

            service_request.completed_at = (
                datetime.now(timezone.utc)
            )

        # =====================================================
        # UPDATE STATUS
        # =====================================================

        service_request.status = new_status

        service_request = (
            ServiceRequestRepository.update(
                db,
                service_request
            )
        )

        # =====================================================
        # HISTORY REMARK
        # =====================================================

        history_remarks = remarks

        if new_status == "Rejected":

            if history_remarks:

                history_remarks = (
                    f"{history_remarks}. "
                    f"Reason: {rejection_reason}"
                )

            else:

                history_remarks = (
                    f"Request rejected. "
                    f"Reason: {rejection_reason}"
                )

        elif new_status == "Completed":

            if history_remarks:

                history_remarks = (
                    f"{history_remarks}. "
                    f"Completion: {completion_notes}"
                )

            else:

                history_remarks = (
                    f"Request completed. "
                    f"Completion: {completion_notes}"
                )

        # -----------------------------------------
        # Create history
        # -----------------------------------------

        ServiceRequestService.add_history(
            db=db,
            request_id=request_id,
            changed_by=changed_by,
            old_status=old_status,
            new_status=new_status,
            remarks=history_remarks
        )

        return service_request

    # =========================================================
    # GET CUSTOMER REQUESTS
    # =========================================================

    @staticmethod
    def get_customer_requests(
        db: Session,
        customer_id: int
    ):

        customer = (
            db.query(Customer)
            .filter(
                Customer.id == customer_id
            )
            .first()
        )

        if not customer:

            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        return (
            ServiceRequestRepository.get_by_customer(
                db,
                customer_id
            )
        )

    # =========================================================
    # GET REQUEST HISTORY
    # =========================================================

    @staticmethod
    def get_request_history(
        db: Session,
        request_id: int
    ):

        # -----------------------------------------
        # Check request
        # -----------------------------------------

        service_request = (
            ServiceRequestRepository.get_by_id(
                db,
                request_id
            )
        )

        if not service_request:

            raise HTTPException(
                status_code=404,
                detail="Service request not found"
            )

        # -----------------------------------------
        # Get history
        # -----------------------------------------

        return (
            ServiceRequestHistoryRepository.get_by_request(
                db,
                request_id
            )
        )

    # =========================================================
    # GET SINGLE REQUEST
    # =========================================================

    @staticmethod
    def get_request(
        db: Session,
        request_id: int
    ):

        service_request = (
            ServiceRequestRepository.get_by_id(
                db,
                request_id
            )
        )

        if not service_request:

            raise HTTPException(
                status_code=404,
                detail="Service request not found"
            )

        return service_request

    # =========================================================
    # GET ASSIGNED REQUESTS
    # =========================================================

    @staticmethod
    def get_assigned_requests(
        db: Session,
        user_id: int
    ):

        # -----------------------------------------
        # Check user
        # -----------------------------------------

        user = (
            db.query(User)
            .filter(
                User.id == user_id
            )
            .first()
        )

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return (
            ServiceRequestRepository.get_by_assigned_user(
                db,
                user_id
            )
        )