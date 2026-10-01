from pydantic import BaseModel


class CustomerDashboard(BaseModel):
    total_customers: int
    active_customers: int


class SubscriptionDashboard(BaseModel):
    active_subscriptions: int


class SIMDashboard(BaseModel):
    active_sims: int


class UsageDashboard(BaseModel):
    total_data_usage: float
    total_voice_usage: float
    total_sms_usage: int


class OutageDashboard(BaseModel):
    total_outages: int
    active_outages: int


class TicketDashboard(BaseModel):
    open_tickets: int
    sla_breaches: int


class TechnicianWorkload(BaseModel):
    technician_id: int
    technician_name: str
    pending_jobs: int
    completed_jobs: int
    total_jobs: int


class TowerDashboard(BaseModel):
    active_towers: int
    maintenance_towers: int
    offline_towers: int
    decommissioned_towers: int


class ServiceRequestDashboard(BaseModel):
    total_requests: int
    submitted: int
    under_review: int
    approved: int
    rejected: int
    in_progress: int
    completed: int
    cancelled: int


class PlanUtilization(BaseModel):
    plan_id: int
    plan_name: str
    total_subscriptions: int
    active_subscriptions: int
    utilization_percentage: float


class OperationsDashboardResponse(BaseModel):

    customers: CustomerDashboard

    subscriptions: SubscriptionDashboard

    sims: SIMDashboard

    usage: UsageDashboard

    outages: OutageDashboard

    tickets: TicketDashboard

    technician_workload: list[TechnicianWorkload]

    towers: TowerDashboard

    service_requests: ServiceRequestDashboard

    plan_utilization: list[PlanUtilization]