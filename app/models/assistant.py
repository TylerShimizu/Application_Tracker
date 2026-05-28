from enum import Enum
from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.db.schema import JobSource, JobStatus
from app.models.job import JobRead


class AssistantIntent(str, Enum):
    list_jobs = "list_jobs"
    count_jobs = "count_jobs"
    list_companies = "list_companies"
    last_application = "last_application"
    days_since_last_application = "days_since_last_application"


class JobQueryFilters(BaseModel):
    status: JobStatus | None = None
    company: str | None = None
    title: str | None = None
    location: str | None = None
    source: JobSource | None = None
    applied_within_days: int | None = Field(default=None, ge=1, le=3650)


class AssistantQuery(BaseModel):
    message: str = Field(min_length=1)


class AssistantPlan(BaseModel):
    intent: AssistantIntent
    filters: JobQueryFilters = Field(default_factory=JobQueryFilters)


class AssistantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    answer: str
    intent: AssistantIntent
    filters: JobQueryFilters
    jobs: list[JobRead] = Field(default_factory=list)
    companies: list[str] = Field(default_factory=list)
    count: int
    last_application_date: date | None = None
    days_since_last_application: int | None = None
