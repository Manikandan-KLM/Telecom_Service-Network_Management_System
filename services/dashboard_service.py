from sqlalchemy import func
from sqlalchemy.orm import Session

from models.customer_model import Customer
from models.subscription_model import Subscription
from models.sim_card_model import SIMCard
from models.usage_model import UsageRecord
from models.network_tower_model import NetworkTower
from models.support_ticket_model import SupportTicket
from models.ticket_sla_model import TicketSLA
from models.service_request_model import ServiceRequest
from models.service_plan_model import ServicePlan
from models.user_model import User


class DashboardService:

    # =========================================================
    # CUSTOMER DASHBOARD
    # =========================================================

    @staticmethod
    def get_customer_dashboard(db: Session):

        total_customers = (
            db.query(func.count(Customer.id))
            .scalar()
            or 0
        )

        active_customers = (
            db.query(func.count(Customer.id))
            .filter(
                Customer.is_active == True
            )
            .scalar()
            or 0
        )

        return {
            "total_customers": total_customers,
            "active_customers": active_customers
        }

    # =========================================================
    # SUBSCRIPTION DASHBOARD
    # =========================================================

    @staticmethod
    def get_subscription_dashboard(db: Session):

        active_subscriptions = (
            db.query(func.count(Subscription.id))
            .filter(
                Subscription.status == "Active"
            )
            .scalar()
            or 0
        )

        return {
            "active_subscriptions": active_subscriptions
        }

    # =========================================================
    # SIM DASHBOARD
    # =========================================================

    @staticmethod
    def get_sim_dashboard(db: Session):

        active_sims = (
            db.query(func.count(SIMCard.id))
            .filter(
                SIMCard.status == "Active"
            )
            .scalar()
            or 0
        )

        return {
            "active_sims": active_sims
        }

    # =========================================================
    # USAGE DASHBOARD
    # =========================================================

    @staticmethod
    def get_usage_dashboard(db: Session):

        data_usage = (
            db.query(
                func.coalesce(
                    func.sum(UsageRecord.usage_amount),
                    0
                )
            )
            .filter(
                UsageRecord.usage_type == "Data"
            )
            .scalar()
            or 0
        )

        voice_usage = (
            db.query(
                func.coalesce(
                    func.sum(UsageRecord.usage_amount),
                    0
                )
            )
            .filter(
                UsageRecord.usage_type == "Voice"
            )
            .scalar()
            or 0
        )

        sms_usage = (
            db.query(
                func.coalesce(
                    func.sum(UsageRecord.usage_amount),
                    0
                )
            )
            .filter(
                UsageRecord.usage_type == "SMS"
            )
            .scalar()
            or 0
        )

        return {
            "total_data_usage": float(data_usage),
            "total_voice_usage": float(voice_usage),
            "total_sms_usage": int(sms_usage)
        }

    # =========================================================
    # OUTAGE DASHBOARD
    # =========================================================

    @staticmethod
    def get_outage_dashboard(db: Session):

        # -----------------------------------------------------
        # IMPORTANT
        # -----------------------------------------------------
        # This assumes your Level 10 NetworkOutage model has:
        #
        # NetworkOutage.id
        # NetworkOutage.status
        #
        # If your actual field names are different,
        # change them here.
        # -----------------------------------------------------

        try:

            from models.network_outage_model import (
                NetworkOutage
            )

        except ImportError:

            return {
                "total_outages": 0,
                "active_outages": 0
            }

        total_outages = (
            db.query(func.count(NetworkOutage.id))
            .scalar()
            or 0
        )

        active_outages = (
            db.query(func.count(NetworkOutage.id))
            .filter(
                NetworkOutage.status == "Active"
            )
            .scalar()
            or 0
        )

        return {
            "total_outages": total_outages,
            "active_outages": active_outages
        }

    # =========================================================
    # TICKET DASHBOARD
    # =========================================================

    @staticmethod
    def get_ticket_dashboard(db: Session):

        open_tickets = (
            db.query(func.count(SupportTicket.id))
            .filter(
                SupportTicket.status.notin_(
                    ["Resolved", "Closed"]
                )
            )
            .scalar()
            or 0
        )

        sla_breaches = (
            db.query(func.count(TicketSLA.id))
            .filter(
                TicketSLA.sla_breached == True
            )
            .scalar()
            or 0
        )

        return {
            "open_tickets": open_tickets,
            "sla_breaches": sla_breaches
        }

    # =========================================================
    # TECHNICIAN WORKLOAD
    # =========================================================

    @staticmethod
    def get_technician_workload(db: Session):

        technicians = (
            db.query(User)
            .filter(
                User.role == "Field Technician",
                User.is_active == True
            )
            .all()
        )

        result = []

        for technician in technicians:

            total_jobs = (
                db.query(func.count(SupportTicket.id))
                .filter(
                    SupportTicket.assigned_technician_id
                    == technician.id
                )
                .scalar()
                or 0
            )

            pending_jobs = (
                db.query(func.count(SupportTicket.id))
                .filter(
                    SupportTicket.assigned_technician_id
                    == technician.id,
                    SupportTicket.status.notin_(
                        ["Resolved", "Closed"]
                    )
                )
                .scalar()
                or 0
            )

            completed_jobs = (
                db.query(func.count(SupportTicket.id))
                .filter(
                    SupportTicket.assigned_technician_id
                    == technician.id,
                    SupportTicket.status.in_(
                        ["Resolved", "Closed"]
                    )
                )
                .scalar()
                or 0
            )

            result.append(
                {
                    "technician_id": technician.id,
                    "technician_name": technician.full_name,
                    "pending_jobs": pending_jobs,
                    "completed_jobs": completed_jobs,
                    "total_jobs": total_jobs
                }
            )

        return result

    # =========================================================
    # TOWER DASHBOARD
    # =========================================================

    @staticmethod
    def get_tower_dashboard(db: Session):

        active_towers = (
            db.query(func.count(NetworkTower.id))
            .filter(
                NetworkTower.status == "Active"
            )
            .scalar()
            or 0
        )

        maintenance_towers = (
            db.query(func.count(NetworkTower.id))
            .filter(
                NetworkTower.status == "Maintenance"
            )
            .scalar()
            or 0
        )

        offline_towers = (
            db.query(func.count(NetworkTower.id))
            .filter(
                NetworkTower.status == "Offline"
            )
            .scalar()
            or 0
        )

        decommissioned_towers = (
            db.query(func.count(NetworkTower.id))
            .filter(
                NetworkTower.status == "Decommissioned"
            )
            .scalar()
            or 0
        )

        return {
            "active_towers": active_towers,
            "maintenance_towers": maintenance_towers,
            "offline_towers": offline_towers,
            "decommissioned_towers":
                decommissioned_towers
        }

    # =========================================================
    # SERVICE REQUEST DASHBOARD
    # =========================================================

    @staticmethod
    def get_service_request_dashboard(
        db: Session
    ):

        total_requests = (
            db.query(func.count(ServiceRequest.id))
            .scalar()
            or 0
        )

        submitted = (
            db.query(func.count(ServiceRequest.id))
            .filter(
                ServiceRequest.status == "Submitted"
            )
            .scalar()
            or 0
        )

        under_review = (
            db.query(func.count(ServiceRequest.id))
            .filter(
                ServiceRequest.status == "Under Review"
            )
            .scalar()
            or 0
        )

        approved = (
            db.query(func.count(ServiceRequest.id))
            .filter(
                ServiceRequest.status == "Approved"
            )
            .scalar()
            or 0
        )

        rejected = (
            db.query(func.count(ServiceRequest.id))
            .filter(
                ServiceRequest.status == "Rejected"
            )
            .scalar()
            or 0
        )

        in_progress = (
            db.query(func.count(ServiceRequest.id))
            .filter(
                ServiceRequest.status == "In Progress"
            )
            .scalar()
            or 0
        )

        completed = (
            db.query(func.count(ServiceRequest.id))
            .filter(
                ServiceRequest.status == "Completed"
            )
            .scalar()
            or 0
        )

        cancelled = (
            db.query(func.count(ServiceRequest.id))
            .filter(
                ServiceRequest.status == "Cancelled"
            )
            .scalar()
            or 0
        )

        return {
            "total_requests": total_requests,
            "submitted": submitted,
            "under_review": under_review,
            "approved": approved,
            "rejected": rejected,
            "in_progress": in_progress,
            "completed": completed,
            "cancelled": cancelled
        }

    # =========================================================
    # PLAN UTILIZATION
    # =========================================================

    @staticmethod
    def get_plan_utilization(db: Session):

        plans = (
            db.query(ServicePlan)
            .filter(
                ServicePlan.is_active == True
            )
            .all()
        )

        result = []

        for plan in plans:

            total_subscriptions = (
                db.query(func.count(Subscription.id))
                .filter(
                    Subscription.plan_id == plan.id
                )
                .scalar()
                or 0
            )

            active_subscriptions = (
                db.query(func.count(Subscription.id))
                .filter(
                    Subscription.plan_id == plan.id,
                    Subscription.status == "Active"
                )
                .scalar()
                or 0
            )

            if total_subscriptions > 0:

                utilization_percentage = (
                    active_subscriptions
                    / total_subscriptions
                ) * 100

            else:

                utilization_percentage = 0.0

            result.append(
                {
                    "plan_id": plan.id,
                    "plan_name": plan.plan_name,
                    "total_subscriptions":
                        total_subscriptions,
                    "active_subscriptions":
                        active_subscriptions,
                    "utilization_percentage":
                        round(
                            utilization_percentage,
                            2
                        )
                }
            )

        return result

    # =========================================================
    # COMPLETE OPERATIONS DASHBOARD
    # =========================================================

    @staticmethod
    def get_operations_dashboard(
        db: Session
    ):

        return {

            "customers":
                DashboardService
                .get_customer_dashboard(db),

            "subscriptions":
                DashboardService
                .get_subscription_dashboard(db),

            "sims":
                DashboardService
                .get_sim_dashboard(db),

            "usage":
                DashboardService
                .get_usage_dashboard(db),

            "outages":
                DashboardService
                .get_outage_dashboard(db),

            "tickets":
                DashboardService
                .get_ticket_dashboard(db),

            "technician_workload":
                DashboardService
                .get_technician_workload(db),

            "towers":
                DashboardService
                .get_tower_dashboard(db),

            "service_requests":
                DashboardService
                .get_service_request_dashboard(db),

            "plan_utilization":
                DashboardService
                .get_plan_utilization(db)
        }