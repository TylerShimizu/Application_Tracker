from pydantic import BaseModel
from datetime import date
from pydantic import ConfigDict

from app.db.schema import JobSource, JobStatus

class JobCreate(BaseModel):
    title: str
    company: str
    status: JobStatus = JobStatus.applied
    source: JobSource | None = None
    location: str | None = None
    date_applied: date | None = None
    job_url: str | None = None
    notes: str | None = None

class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    company: str
    status: JobStatus
    source: JobSource | None = None
    location: str | None = None
    date_applied: date | None = None
    job_url: str | None = None
    notes: str | None = None

class JobUpdate(BaseModel):
    title: str | None = None
    company: str | None = None
    status: JobStatus | None = None
    source: JobSource | None = None
    location: str | None = None
    date_applied: date | None = None
    job_url: str | None = None
    notes: str | None = None
