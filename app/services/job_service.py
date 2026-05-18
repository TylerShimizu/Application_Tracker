from sqlalchemy.orm import Session

from app.db.schema import Job

class JobService:
    """Service for managing jobs."""

    def __init__(self, session: Session):
        self._db = session

    def list_jobs(self, user_id: int) -> list[Job]:
        return self._db.query(Job).filter(Job.user_id == user_id).all()

    def create_job(self, title: str, company: str, status: str, user_id: int, location: str | None = None, date_applied: str | None = None, job_url: str | None = None) -> Job:
        """Create a new job."""
        job = Job(title=title, company=company, status=status, user_id=user_id, location=location, date_applied=date_applied, job_url=job_url)
        self._db.add(job)
        self._db.commit()
        self._db.refresh(job)
        return job

    def get_job(self, job_id: int, user_id: int) -> Job:
        """Get a job by ID."""
        job = self._db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()
        if not job:
            return None
        return job

    def update_job(self, job_id: int, user_id: int, title: str | None = None, company: str | None = None, status: str | None = None, location: str | None = None, date_applied: str | None = None, job_url: str | None = None) -> Job | None:
        """Update a job."""
        job = self._db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()
        if not job:
            return None
        if title is not None:
            job.title = title
        if company is not None:
            job.company = company
        if status is not None:
            job.status = status
        if location is not None:
            job.location = location
        if date_applied is not None:
            job.date_applied = date_applied
        if job_url is not None:
            job.job_url = job_url
        self._db.commit()
        self._db.refresh(job)
        return job
    
    def delete_job(self, job_id: int, user_id: int) -> bool:
        """Delete a job by ID."""
        job = self._db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()
        if not job:
            return False
        self._db.delete(job)
        self._db.commit()
        return True