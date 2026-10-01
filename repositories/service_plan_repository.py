from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.service_plan_model import ServicePlan


class ServicePlanRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        plan_id: int
    ) -> ServicePlan | None:

        return (
            db.query(ServicePlan)
            .filter(
                ServicePlan.id == plan_id
            )
            .first()
        )

    @staticmethod
    def get_by_code(
        db: Session,
        plan_code: str
    ) -> ServicePlan | None:

        return (
            db.query(ServicePlan)
            .filter(
                ServicePlan.plan_code == plan_code
            )
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        plan: ServicePlan
    ) -> ServicePlan:

        db.add(plan)
        db.commit()
        db.refresh(plan)

        return plan

    @staticmethod
    def update(
        db: Session,
        plan: ServicePlan
    ) -> ServicePlan:

        db.commit()
        db.refresh(plan)

        return plan

    @staticmethod
    def search(
        db: Session,
        search: str | None = None,
        plan_type: str | None = None,
        is_active: bool | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        min_validity: int | None = None
    ):

        query = db.query(ServicePlan)

        if search:

            search_value = f"%{search}%"

            query = query.filter(
                or_(
                    ServicePlan.plan_code.ilike(
                        search_value
                    ),
                    ServicePlan.plan_name.ilike(
                        search_value
                    )
                )
            )

        if plan_type:

            query = query.filter(
                ServicePlan.plan_type == plan_type
            )

        if is_active is not None:

            query = query.filter(
                ServicePlan.is_active == is_active
            )

        if min_price is not None:

            query = query.filter(
                ServicePlan.price >= min_price
            )

        if max_price is not None:

            query = query.filter(
                ServicePlan.price <= max_price
            )

        if min_validity is not None:

            query = query.filter(
                ServicePlan.validity_days >= min_validity
            )

        return (
            query
            .order_by(ServicePlan.price.asc())
            .all()
        )

    @staticmethod
    def get_multiple_by_ids(
        db: Session,
        plan_ids: list[int]
    ):

        return (
            db.query(ServicePlan)
            .filter(
                ServicePlan.id.in_(plan_ids)
            )
            .all()
        )