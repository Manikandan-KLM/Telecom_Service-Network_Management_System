from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.technician_model import Technician
from models.technician_assignment_model import (
    TechnicianAssignment
)

from repositories.technician_repository import (
    TechnicianRepository
)

from repositories.technician_assignment_repository import (
    TechnicianAssignmentRepository
)

from repositories.technician_mapping_repository import (
    TechnicianMappingRepository
)


class TechnicianService:

    AVAILABILITY_STATUSES = {
        "Available",
        "Busy",
        "On Leave",
        "Offline"
    }

    SKILL_LEVELS = {
        "Beginner",
        "Intermediate",
        "Advanced",
        "Expert"
    }

    JOB_STATUSES = {
        "Pending",
        "In Progress",
        "Completed",
        "Cancelled"
    }

    JOB_TYPES = {
        "Outage Repair",
        "Installation",
        "Maintenance",
        "Equipment Repair",
        "Network Inspection",
        "Customer Service",
        "Other"
    }

    # =================================================
    # VALIDATIONS
    # =================================================

    @staticmethod
    def validate_availability(
        status: str
    ):

        if status not in TechnicianService.AVAILABILITY_STATUSES:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid availability status"
                )
            )

    @staticmethod
    def validate_skill_level(
        level: str
    ):

        if level not in TechnicianService.SKILL_LEVELS:

            raise HTTPException(
                status_code=400,
                detail="Invalid skill level"
            )

    @staticmethod
    def validate_job_type(
        job_type: str
    ):

        if job_type not in TechnicianService.JOB_TYPES:

            raise HTTPException(
                status_code=400,
                detail="Invalid job type"
            )

    @staticmethod
    def validate_job_status(
        status: str
    ):

        if status not in TechnicianService.JOB_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid job status"
            )

    # =================================================
    # REGISTER TECHNICIAN
    # =================================================

    @staticmethod
    def create_technician(
        db: Session,
        user_id: int,
        technician_code: str,
        full_name: str,
        phone: str,
        availability_status: str,
        latitude: float | None,
        longitude: float | None,
        service_area: str
    ):

        TechnicianService.validate_availability(
            availability_status
        )

        existing_code = (
            TechnicianRepository.get_by_code(
                db,
                technician_code.upper()
            )
        )

        if existing_code:

            raise HTTPException(
                status_code=409,
                detail="Technician code already exists"
            )

        existing_user = (
            TechnicianRepository.get_by_user_id(
                db,
                user_id
            )
        )

        if existing_user:

            raise HTTPException(
                status_code=409,
                detail="User is already registered as technician"
            )

        technician = Technician(
            user_id=user_id,
            technician_code=technician_code.upper(),
            full_name=full_name,
            phone=phone,
            availability_status=availability_status,
            latitude=latitude,
            longitude=longitude,
            service_area=service_area,
            is_active=True
        )

        return TechnicianRepository.create(
            db,
            technician
        )

    # =================================================
    # UPDATE TECHNICIAN
    # =================================================

    @staticmethod
    def update_technician(
        db: Session,
        technician_id: int,
        phone: str | None = None,
        availability_status: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        service_area: str | None = None,
        is_active: bool | None = None
    ):

        technician = (
            TechnicianRepository.get_by_id(
                db,
                technician_id
            )
        )

        if not technician:

            raise HTTPException(
                status_code=404,
                detail="Technician not found"
            )

        if availability_status:

            TechnicianService.validate_availability(
                availability_status
            )

            technician.availability_status = (
                availability_status
            )

        if phone is not None:
            technician.phone = phone

        if latitude is not None:
            technician.latitude = latitude

        if longitude is not None:
            technician.longitude = longitude

        if service_area is not None:
            technician.service_area = service_area

        if is_active is not None:
            technician.is_active = is_active

        return TechnicianRepository.update(
            db,
            technician
        )

    # =================================================
    # ADD SKILL
    # =================================================

    @staticmethod
    def add_skill(
        db: Session,
        technician_id: int,
        skill_name: str,
        skill_level: str
    ):

        technician = (
            TechnicianRepository.get_by_id(
                db,
                technician_id
            )
        )

        if not technician:

            raise HTTPException(
                status_code=404,
                detail="Technician not found"
            )

        TechnicianService.validate_skill_level(
            skill_level
        )

        return TechnicianMappingRepository.add_skill(
            db,
            technician_id,
            skill_name,
            skill_level
        )

    # =================================================
    # ADD SERVICE AREA
    # =================================================

    @staticmethod
    def add_service_area(
        db: Session,
        technician_id: int,
        area_name: str
    ):

        technician = (
            TechnicianRepository.get_by_id(
                db,
                technician_id
            )
        )

        if not technician:

            raise HTTPException(
                status_code=404,
                detail="Technician not found"
            )

        return TechnicianMappingRepository.add_service_area(
            db,
            technician_id,
            area_name
        )

    # =================================================
    # ASSIGN TECHNICIAN
    # =================================================

    @staticmethod
    def assign_technician(
        db: Session,
        technician_id: int,
        job_type: str,
        outage_id: int | None,
        customer_id: int | None,
        job_description: str | None
    ):

        technician = (
            TechnicianRepository.get_by_id(
                db,
                technician_id
            )
        )

        if not technician:

            raise HTTPException(
                status_code=404,
                detail="Technician not found"
            )

        if not technician.is_active:

            raise HTTPException(
                status_code=400,
                detail="Technician is inactive"
            )

        if technician.availability_status in {
            "On Leave",
            "Offline"
        }:

            raise HTTPException(
                status_code=400,
                detail="Technician is not available"
            )

        TechnicianService.validate_job_type(
            job_type
        )

        if not outage_id and not customer_id:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Either outage_id or customer_id "
                    "is required"
                )
            )

        assignment = TechnicianAssignment(
            technician_id=technician_id,
            outage_id=outage_id,
            customer_id=customer_id,
            job_type=job_type,
            job_description=job_description,
            status="Pending"
        )

        result = (
            TechnicianAssignmentRepository.create(
                db,
                assignment
            )
        )

        # Technician becomes busy
        technician.availability_status = "Busy"

        TechnicianRepository.update(
            db,
            technician
        )

        return result

    # =================================================
    # REASSIGN TECHNICIAN
    # =================================================

    @staticmethod
    def reassign_technician(
        db: Session,
        assignment_id: int,
        new_technician_id: int
    ):

        assignment = (
            TechnicianAssignmentRepository.get_by_id(
                db,
                assignment_id
            )
        )

        if not assignment:

            raise HTTPException(
                status_code=404,
                detail="Assignment not found"
            )

        new_technician = (
            TechnicianRepository.get_by_id(
                db,
                new_technician_id
            )
        )

        if not new_technician:

            raise HTTPException(
                status_code=404,
                detail="New technician not found"
            )

        if not new_technician.is_active:

            raise HTTPException(
                status_code=400,
                detail="New technician is inactive"
            )

        if new_technician.availability_status in {
            "On Leave",
            "Offline"
        }:

            raise HTTPException(
                status_code=400,
                detail="New technician is not available"
            )

        old_technician_id = assignment.technician_id

        assignment.technician_id = new_technician_id

        updated = (
            TechnicianAssignmentRepository.update(
                db,
                assignment
            )
        )

        # New technician becomes busy
        new_technician.availability_status = "Busy"

        TechnicianRepository.update(
            db,
            new_technician
        )

        # Old technician can become available
        old_technician = (
            TechnicianRepository.get_by_id(
                db,
                old_technician_id
            )
        )

        if old_technician:

            pending = (
                TechnicianAssignmentRepository
                .count_by_status(
                    db,
                    old_technician_id,
                    "Pending"
                )
            )

            in_progress = (
                TechnicianAssignmentRepository
                .count_by_status(
                    db,
                    old_technician_id,
                    "In Progress"
                )
            )

            if pending == 0 and in_progress == 0:

                old_technician.availability_status = (
                    "Available"
                )

                TechnicianRepository.update(
                    db,
                    old_technician
                )

        return updated

    # =================================================
    # UPDATE JOB STATUS
    # =================================================

    @staticmethod
    def update_assignment_status(
        db: Session,
        assignment_id: int,
        status: str,
        notes: str | None = None
    ):

        assignment = (
            TechnicianAssignmentRepository.get_by_id(
                db,
                assignment_id
            )
        )

        if not assignment:

            raise HTTPException(
                status_code=404,
                detail="Assignment not found"
            )

        TechnicianService.validate_job_status(
            status
        )

        now = datetime.now(timezone.utc)

        assignment.status = status

        if notes is not None:
            assignment.notes = notes

        if status == "In Progress":

            assignment.started_at = now

        if status == "Completed":

            assignment.completed_at = now

        result = (
            TechnicianAssignmentRepository.update(
                db,
                assignment
            )
        )

        # Update technician availability
        technician = (
            TechnicianRepository.get_by_id(
                db,
                assignment.technician_id
            )
        )

        if technician:

            pending = (
                TechnicianAssignmentRepository
                .count_by_status(
                    db,
                    technician.id,
                    "Pending"
                )
            )

            in_progress = (
                TechnicianAssignmentRepository
                .count_by_status(
                    db,
                    technician.id,
                    "In Progress"
                )
            )

            if pending == 0 and in_progress == 0:

                technician.availability_status = (
                    "Available"
                )

            else:

                technician.availability_status = "Busy"

            TechnicianRepository.update(
                db,
                technician
            )

        return result

    # =================================================
    # WORKLOAD
    # =================================================

    @staticmethod
    def get_workload(
        db: Session,
        technician_id: int
    ):

        technician = (
            TechnicianRepository.get_by_id(
                db,
                technician_id
            )
        )

        if not technician:

            raise HTTPException(
                status_code=404,
                detail="Technician not found"
            )

        pending = (
            TechnicianAssignmentRepository
            .count_by_status(
                db,
                technician_id,
                "Pending"
            )
        )

        in_progress = (
            TechnicianAssignmentRepository
            .count_by_status(
                db,
                technician_id,
                "In Progress"
            )
        )

        completed = (
            TechnicianAssignmentRepository
            .count_by_status(
                db,
                technician_id,
                "Completed"
            )
        )

        total = pending + in_progress + completed

        return {
            "technician_id": technician.id,
            "technician_code": technician.technician_code,
            "technician_name": technician.full_name,
            "pending_jobs": pending,
            "in_progress_jobs": in_progress,
            "completed_jobs": completed,
            "total_jobs": total
        }

    # =================================================
    # JOB LIST
    # =================================================

    @staticmethod
    def get_jobs(
        db: Session,
        technician_id: int,
        status: str | None = None
    ):

        jobs = (
            TechnicianAssignmentRepository
            .get_by_technician(
                db,
                technician_id
            )
        )

        if status:

            TechnicianService.validate_job_status(
                status
            )

            jobs = [
                job
                for job in jobs
                if job.status == status
            ]

        return jobs