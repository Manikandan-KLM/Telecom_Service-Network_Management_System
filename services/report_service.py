from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from models.customer_model import Customer
from models.subscription_model import Subscription
from models.service_plan_model import ServicePlan
from models.usage_model import UsageRecord
from models.support_ticket_model import SupportTicket
from models.ticket_sla_model import TicketSLA
from models.service_request_model import ServiceRequest
from models.user_model import User


class ReportService:

    # =========================================================
    # COMMON DATE HELPERS
    # =========================================================

    @staticmethod
    def get_start_datetime(
        start_date: date | None
    ):

        if start_date:

            return datetime(
                start_date.year,
                start_date.month,
                start_date.day,
                tzinfo=timezone.utc
            )

        return datetime(
            2000,
            1,
            1,
            tzinfo=timezone.utc
        )

    @staticmethod
    def get_end_datetime(
        end_date: date | None
    ):

        if end_date:

            return datetime(
                end_date.year,
                end_date.month,
                end_date.day,
                23,
                59,
                59,
                tzinfo=timezone.utc
            )

        return datetime.now(timezone.utc)

    # =========================================================
    # VALIDATE DATE RANGE
    # =========================================================

    @staticmethod
    def validate_date_range(
        start_date: date | None,
        end_date: date | None
    ):

        if start_date and end_date:

            if start_date > end_date:

                raise ValueError(
                    "start_date cannot be greater than end_date"
                )

    # =========================================================
    # PAGINATION
    # =========================================================

    @staticmethod
    def paginate(
        query,
        page: int,
        limit: int
    ):

        total = query.count()

        offset = (page - 1) * limit

        records = (
            query
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "items": records,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (
                (total + limit - 1) // limit
                if total > 0
                else 0
            )
        }

    # =========================================================
    # 1. CUSTOMER GROWTH
    # =========================================================

    @staticmethod
    def customer_growth(
        db: Session,
        start_date: date | None = None,
        end_date: date | None = None,
        customer_id: int | None = None,
        location: str | None = None
    ):

        ReportService.validate_date_range(
            start_date,
            end_date
        )

        start = ReportService.get_start_datetime(
            start_date
        )

        end = ReportService.get_end_datetime(
            end_date
        )

        query = db.query(Customer)

        query = query.filter(
            Customer.created_at >= start,
            Customer.created_at <= end
        )

        if customer_id:

            query = query.filter(
                Customer.id == customer_id
            )

        if location:

            location_pattern = f"%{location}%"

            query = query.filter(
                or_(
                    Customer.city.ilike(
                        location_pattern
                    ),
                    Customer.state.ilike(
                        location_pattern
                    ),
                    Customer.country.ilike(
                        location_pattern
                    )
                )
            )

        customers = query.all()

        monthly_data = {}

        for customer in customers:

            period = customer.created_at.strftime(
                "%Y-%m"
            )

            monthly_data[period] = (
                monthly_data.get(period, 0) + 1
            )

        result = []

        running_total = 0

        for period in sorted(monthly_data):

            new_customers = monthly_data[period]

            running_total += new_customers

            result.append(
                {
                    "period": period,
                    "new_customers": new_customers,
                    "total_customers": running_total
                }
            )

        return result

    # =========================================================
    # 2. SUBSCRIPTION TRENDS
    # =========================================================

    @staticmethod
    def subscription_trends(
        db: Session,
        start_date: date | None = None,
        end_date: date | None = None,
        customer_id: int | None = None,
        plan_id: int | None = None,
        status: str | None = None
    ):

        ReportService.validate_date_range(
            start_date,
            end_date
        )

        start = ReportService.get_start_datetime(
            start_date
        )

        end = ReportService.get_end_datetime(
            end_date
        )

        query = db.query(Subscription)

        query = query.filter(
            Subscription.start_date >= start,
            Subscription.start_date <= end
        )

        if customer_id:

            query = query.filter(
                Subscription.customer_id == customer_id
            )

        if plan_id:

            query = query.filter(
                Subscription.plan_id == plan_id
            )

        if status:

            query = query.filter(
                Subscription.status == status
            )

        subscriptions = query.all()

        monthly_data = {}

        for subscription in subscriptions:

            period = subscription.start_date.strftime(
                "%Y-%m"
            )

            if period not in monthly_data:

                monthly_data[period] = {
                    "new_subscriptions": 0,
                    "active_subscriptions": 0
                }

            monthly_data[period][
                "new_subscriptions"
            ] += 1

            if subscription.status == "Active":

                monthly_data[period][
                    "active_subscriptions"
                ] += 1

        result = []

        for period in sorted(monthly_data):

            result.append(
                {
                    "period": period,
                    **monthly_data[period]
                }
            )

        return result

    # =========================================================
    # 3. PLAN POPULARITY
    # =========================================================

    @staticmethod
    def plan_popularity(
        db: Session,
        start_date: date | None = None,
        end_date: date | None = None,
        plan_id: int | None = None,
        customer_id: int | None = None,
        search: str | None = None
    ):

        query = (
            db.query(
                ServicePlan.id,
                ServicePlan.plan_name,
                func.count(
                    Subscription.id
                ).label(
                    "total_subscriptions"
                )
            )
            .outerjoin(
                Subscription,
                Subscription.plan_id
                == ServicePlan.id
            )
            .group_by(
                ServicePlan.id,
                ServicePlan.plan_name
            )
        )

        if plan_id:

            query = query.filter(
                ServicePlan.id == plan_id
            )

        if customer_id:

            query = query.filter(
                Subscription.customer_id
                == customer_id
            )

        if search:

            query = query.filter(
                ServicePlan.plan_name.ilike(
                    f"%{search}%"
                )
            )

        rows = query.all()

        total_subscriptions = sum(
            row.total_subscriptions
            for row in rows
        )

        result = []

        for row in rows:

            active_count = (
                db.query(
                    func.count(Subscription.id)
                )
                .filter(
                    Subscription.plan_id == row.id,
                    Subscription.status == "Active"
                )
                .scalar()
                or 0
            )

            if total_subscriptions > 0:

                popularity = (
                    row.total_subscriptions
                    / total_subscriptions
                ) * 100

            else:

                popularity = 0.0

            result.append(
                {
                    "plan_id": row.id,
                    "plan_name": row.plan_name,
                    "total_subscriptions":
                        row.total_subscriptions,
                    "active_subscriptions":
                        active_count,
                    "popularity_percentage":
                        round(
                            popularity,
                            2
                        )
                }
            )

        return result

    # =========================================================
    # 4. DATA CONSUMPTION
    # =========================================================

    @staticmethod
    def data_consumption(
        db: Session,
        start_date: date | None = None,
        end_date: date | None = None,
        customer_id: int | None = None
    ):

        start = ReportService.get_start_datetime(
            start_date
        )

        end = ReportService.get_end_datetime(
            end_date
        )

        query = db.query(UsageRecord).filter(
            UsageRecord.usage_type == "Data",
            UsageRecord.usage_date >= start,
            UsageRecord.usage_date <= end
        )

        if customer_id:

            query = query.filter(
                UsageRecord.customer_id
                == customer_id
            )

        records = query.all()

        monthly_data = {}

        for record in records:

            period = record.usage_date.strftime(
                "%Y-%m"
            )

            monthly_data[period] = (
                monthly_data.get(period, 0)
                + record.usage_amount
            )

        result = []

        for period in sorted(monthly_data):

            result.append(
                {
                    "period": period,
                    "total_data_usage":
                        round(
                            monthly_data[period],
                            2
                        )
                }
            )

        return result

    # =========================================================
    # 5. NETWORK UPTIME
    # =========================================================

    @staticmethod
    def network_uptime(
        db: Session
    ):

        try:

            from models.network_equipment_model import (
                NetworkEquipment
            )

        except ImportError:

            return {
                "total_equipment": 0,
                "online_equipment": 0,
                "offline_equipment": 0,
                "uptime_percentage": 0.0
            }

        total_equipment = (
            db.query(
                func.count(
                    NetworkEquipment.id
                )
            )
            .scalar()
            or 0
        )

        online_equipment = (
            db.query(
                func.count(
                    NetworkEquipment.id
                )
            )
            .filter(
                NetworkEquipment.network_status
                == "Online"
            )
            .scalar()
            or 0
        )

        offline_equipment = (
            db.query(
                func.count(
                    NetworkEquipment.id
                )
            )
            .filter(
                NetworkEquipment.network_status
                == "Offline"
            )
            .scalar()
            or 0
        )

        if total_equipment > 0:

            uptime = (
                online_equipment
                / total_equipment
            ) * 100

        else:

            uptime = 0.0

        return {
            "total_equipment": total_equipment,
            "online_equipment": online_equipment,
            "offline_equipment": offline_equipment,
            "uptime_percentage":
                round(uptime, 2)
        }

    # =========================================================
    # 6. OUTAGE FREQUENCY
    # =========================================================

    @staticmethod
    def outage_frequency(
        db: Session,
        start_date: date | None = None,
        end_date: date | None = None
    ):

        try:

            from models.network_outage_model import (
                NetworkOutage
            )

        except ImportError:

            return []

        start = ReportService.get_start_datetime(
            start_date
        )

        end = ReportService.get_end_datetime(
            end_date
        )

        query = (
            db.query(NetworkOutage)
            .filter(
                NetworkOutage.start_time >= start,
                NetworkOutage.start_time <= end
            )
        )

        outages = query.all()

        monthly_data = {}

        for outage in outages:

            period = outage.start_time.strftime(
                "%Y-%m"
            )

            monthly_data[period] = (
                monthly_data.get(period, 0) + 1
            )

        result = []

        for period in sorted(monthly_data):

            result.append(
                {
                    "period": period,
                    "outage_count":
                        monthly_data[period]
                }
            )

        return result

    # =========================================================
    # 7. TICKET RESOLUTION TIME
    # =========================================================

    @staticmethod
    def ticket_resolution_time(
        db: Session,
        start_date: date | None = None,
        end_date: date | None = None,
        status: str | None = None
    ):

        start = ReportService.get_start_datetime(
            start_date
        )

        end = ReportService.get_end_datetime(
            end_date
        )

        query = db.query(SupportTicket).filter(
            SupportTicket.resolved_at.isnot(None),
            SupportTicket.created_at >= start,
            SupportTicket.created_at <= end
        )

        if status:

            query = query.filter(
                SupportTicket.status == status
            )

        tickets = query.all()

        resolution_times = []

        for ticket in tickets:

            if not ticket.resolved_at:

                continue

            created = ticket.created_at
            resolved = ticket.resolved_at

            minutes = (
                resolved - created
            ).total_seconds() / 60

            resolution_times.append(
                minutes
            )

        total = len(resolution_times)

        if total > 0:

            average = (
                sum(resolution_times)
                / total
            )

            minimum = min(
                resolution_times
            )

            maximum = max(
                resolution_times
            )

        else:

            average = 0.0
            minimum = None
            maximum = None

        return {
            "total_resolved_tickets": total,
            "average_resolution_minutes":
                round(average, 2),
            "minimum_resolution_minutes":
                minimum,
            "maximum_resolution_minutes":
                maximum
        }

    # =========================================================
    # 8. SLA PERFORMANCE
    # =========================================================

    @staticmethod
    def sla_performance(
        db: Session,
        start_date: date | None = None,
        end_date: date | None = None
    ):

        start = ReportService.get_start_datetime(
            start_date
        )

        end = ReportService.get_end_datetime(
            end_date
        )

        query = (
            db.query(TicketSLA)
            .filter(
                TicketSLA.sla_start_time >= start,
                TicketSLA.sla_start_time <= end
            )
        )

        records = query.all()

        total = len(records)

        breached = sum(
            1
            for record in records
            if record.sla_breached
        )

        successful = total - breached

        if total > 0:

            success_percentage = (
                successful / total
            ) * 100

            breach_percentage = (
                breached / total
            ) * 100

        else:

            success_percentage = 0.0
            breach_percentage = 0.0

        return {
            "total_sla_tickets": total,
            "breached_tickets": breached,
            "successful_tickets": successful,
            "sla_success_percentage":
                round(
                    success_percentage,
                    2
                ),
            "sla_breach_percentage":
                round(
                    breach_percentage,
                    2
                )
        }

    # =========================================================
    # 9. TECHNICIAN PERFORMANCE
    # =========================================================

    @staticmethod
    def technician_performance(
        db: Session,
        technician_id: int | None = None,
        search: str | None = None
    ):

        technicians = (
            db.query(User)
            .filter(
                User.role == "Field Technician"
            )
        )

        if technician_id:

            technicians = technicians.filter(
                User.id == technician_id
            )

        if search:

            technicians = technicians.filter(
                User.full_name.ilike(
                    f"%{search}%"
                )
            )

        technicians = technicians.all()

        result = []

        for technician in technicians:

            total_jobs = (
                db.query(
                    func.count(
                        SupportTicket.id
                    )
                )
                .filter(
                    SupportTicket.assigned_technician_id
                    == technician.id
                )
                .scalar()
                or 0
            )

            completed_jobs = (
                db.query(
                    func.count(
                        SupportTicket.id
                    )
                )
                .filter(
                    SupportTicket.assigned_technician_id
                    == technician.id,
                    SupportTicket.status.in_(
                        [
                            "Resolved",
                            "Closed"
                        ]
                    )
                )
                .scalar()
                or 0
            )

            pending_jobs = (
                total_jobs
                - completed_jobs
            )

            if total_jobs > 0:

                completion_percentage = (
                    completed_jobs
                    / total_jobs
                ) * 100

            else:

                completion_percentage = 0.0

            result.append(
                {
                    "technician_id":
                        technician.id,
                    "technician_name":
                        technician.full_name,
                    "total_jobs":
                        total_jobs,
                    "completed_jobs":
                        completed_jobs,
                    "pending_jobs":
                        pending_jobs,
                    "completion_percentage":
                        round(
                            completion_percentage,
                            2
                        )
                }
            )

        return result

    # =========================================================
    # 10. CUSTOMER SERVICE TRENDS
    # =========================================================

    @staticmethod
    def customer_service_trends(
        db: Session,
        start_date: date | None = None,
        end_date: date | None = None,
        customer_id: int | None = None,
        status: str | None = None
    ):

        start = ReportService.get_start_datetime(
            start_date
        )

        end = ReportService.get_end_datetime(
            end_date
        )

        query = (
            db.query(ServiceRequest)
            .filter(
                ServiceRequest.created_at >= start,
                ServiceRequest.created_at <= end
            )
        )

        if customer_id:

            query = query.filter(
                ServiceRequest.customer_id
                == customer_id
            )

        if status:

            query = query.filter(
                ServiceRequest.status == status
            )

        requests = query.all()

        monthly_data = {}

        for request in requests:

            period = request.created_at.strftime(
                "%Y-%m"
            )

            if period not in monthly_data:

                monthly_data[period] = {
                    "total_requests": 0,
                    "completed_requests": 0,
                    "rejected_requests": 0,
                    "cancelled_requests": 0
                }

            monthly_data[period][
                "total_requests"
            ] += 1

            if request.status == "Completed":

                monthly_data[period][
                    "completed_requests"
                ] += 1

            elif request.status == "Rejected":

                monthly_data[period][
                    "rejected_requests"
                ] += 1

            elif request.status == "Cancelled":

                monthly_data[period][
                    "cancelled_requests"
                ] += 1

        result = []

        for period in sorted(monthly_data):

            result.append(
                {
                    "period": period,
                    **monthly_data[period]
                }
            )

        return result