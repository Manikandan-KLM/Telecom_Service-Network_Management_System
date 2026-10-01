from sqlalchemy.orm import Session

from models.technician_skill_model import (
    TechnicianSkill
)

from models.technician_service_area_model import (
    TechnicianServiceArea
)


class TechnicianMappingRepository:

    # =================================================
    # SKILL
    # =================================================

    @staticmethod
    def add_skill(
        db: Session,
        technician_id: int,
        skill_name: str,
        skill_level: str
    ):

        skill = TechnicianSkill(
            technician_id=technician_id,
            skill_name=skill_name,
            skill_level=skill_level
        )

        db.add(skill)
        db.commit()
        db.refresh(skill)

        return skill

    @staticmethod
    def get_skills(
        db: Session,
        technician_id: int
    ):

        return (
            db.query(TechnicianSkill)
            .filter(
                TechnicianSkill.technician_id
                == technician_id
            )
            .all()
        )

    # =================================================
    # SERVICE AREA
    # =================================================

    @staticmethod
    def add_service_area(
        db: Session,
        technician_id: int,
        area_name: str
    ):

        area = TechnicianServiceArea(
            technician_id=technician_id,
            area_name=area_name
        )

        db.add(area)
        db.commit()
        db.refresh(area)

        return area

    @staticmethod
    def get_service_areas(
        db: Session,
        technician_id: int
    ):

        return (
            db.query(TechnicianServiceArea)
            .filter(
                TechnicianServiceArea.technician_id
                == technician_id
            )
            .all()
        )