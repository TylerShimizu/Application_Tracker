from pydantic import BaseModel
from datetime import date

from app.db.schema import JobStatus

class JobCreate(BaseModel):
    user_id: int
    title: str
    company: str
    status: JobStatus.applied
    location: str | None = None
    date_applied: date | None = None
    job_url: str | None = None

class JobRead(BaseModel):
    id: int
    user_id: int
    title: str
    company: str
    status: JobStatus
    location: str | None = None
    date_applied: date | None = None
    job_url: str | None = None

class JobUpdate(BaseModel):
    title: str | None = None
    company: str | None = None
    status: JobStatus | None = None
    location: str | None = None
    date_applied: date | None = None
    job_url: str | None = None