from datetime import date, datetime

from pydantic import BaseModel, Field


class ReportQueryParams(BaseModel):
    start_date: date | None = None
    end_date: date | None = None

    customer_id: int | None = None
    plan_id: int | None = None

    location: str | None = None

    status: str | None = None

    search: str | None = None

    page: int = Field(
        default=1,
        ge=1
    )

    limit: int = Field(
        default=20,
        ge=1,
        le=100
    )

    sort_by: str = "created_at"

    sort_order: str = "desc"


class CustomerGrowthReport(BaseModel):
    period: str
    new_customers: int
    total_customers: int


class SubscriptionTrendReport(BaseModel):
    period: str
    new_subscriptions: int
    active_subscriptions: int


class PlanPopularityReport(BaseModel):
    plan_id: int
    plan_name: str
    total_subscriptions: int
    active_subscriptions: int
    popularity_percentage: float


class DataConsumptionReport(BaseModel):
    period: str
    total_data_usage: float


class NetworkUptimeReport(BaseModel):
    total_equipment: int
    online_equipment: int
    offline_equipment: int
    uptime_percentage: float


class OutageFrequencyReport(BaseModel):
    period: str
    outage_count: int


class TicketResolutionReport(BaseModel):
    total_resolved_tickets: int
    average_resolution_minutes: float
    minimum_resolution_minutes: float | None
    maximum_resolution_minutes: float | None


class SLAPerformanceReport(BaseModel):
    total_sla_tickets: int
    breached_tickets: int
    successful_tickets: int
    sla_success_percentage: float
    sla_breach_percentage: float


class TechnicianPerformanceReport(BaseModel):
    technician_id: int
    technician_name: str
    total_jobs: int
    completed_jobs: int
    pending_jobs: int
    completion_percentage: float


class CustomerServiceTrendReport(BaseModel):
    period: str
    total_requests: int
    completed_requests: int
    rejected_requests: int
    cancelled_requests: int