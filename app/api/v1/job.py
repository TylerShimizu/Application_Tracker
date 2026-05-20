from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.db.schema import User
from app.models.job import JobCreate, JobRead, JobUpdate
from app.services.job_service import JobService

router = APIRouter()

def get_job_service(db: Session = Depends(get_db)) -> JobService:
    return JobService(session=db)

@router.get("/jobs", response_model=list[JobRead])
def get_jobs(
    current_user: User = Depends(get_current_user),
    service: JobService = Depends(get_job_service),
):
    """Get a list of all jobs for a user."""
    return service.list_jobs(user_id=current_user.id)

@router.post("/jobs", response_model=JobRead)
def create_job(
    job: JobCreate,
    current_user: User = Depends(get_current_user),
    service: JobService = Depends(get_job_service),
):
    """Create a new job."""
    created_job = service.create_job(title=job.title, 
                                     company=job.company, 
                                     status=job.status, 
                                     user_id=current_user.id,
                                     location=job.location, 
                                     date_applied=job.date_applied, 
                                     job_url=job.job_url)
    if not created_job:
        raise HTTPException(status_code=404, detail="User not found")
    return created_job

@router.get("/jobs/{job_id}", response_model=JobRead)
def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    service: JobService = Depends(get_job_service),
):
    """Get a job by ID."""
    job = service.get_job(job_id=job_id, user_id=current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.put("/jobs/{job_id}", response_model=JobRead)
def update_job(
    job_id: int,
    job: JobUpdate,
    current_user: User = Depends(get_current_user),
    service: JobService = Depends(get_job_service),
):
    """Update a job."""
    updated_job = service.update_job(job_id=job_id, 
                                     user_id=current_user.id,
                                     title=job.title, 
                                     company=job.company, 
                                     status=job.status, 
                                     location=job.location, 
                                     date_applied=job.date_applied, 
                                     job_url=job.job_url)
    if not updated_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return updated_job

@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    service: JobService = Depends(get_job_service),
):
    """Delete a job by ID."""
    success = service.delete_job(job_id=job_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"detail": "Job deleted successfully"}
