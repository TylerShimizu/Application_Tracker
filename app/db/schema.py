import enum
from datetime import date

from sqlalchemy import Date, Enum as SqlEnum, ForeignKey, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from app.core.config import config

engine = create_engine(config.DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    jobs: Mapped[list["Job"]] = relationship("Job", back_populates="user", cascade="all, delete-orphan")

class JobStatus(str, enum.Enum):
    applied = "applied"
    interviewing = "interviewing"
    offered = "offered"
    rejected = "rejected"
    interested = "interested"

class JobSource(str, enum.Enum):
    linkedin = "linkedin"
    indeed = "indeed"
    company_site = "company_site"
    referral = "referral"
    recruiter = "recruiter"
    other = "other"

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    user: Mapped["User"] = relationship("User", back_populates="jobs")
    title: Mapped[str] = mapped_column(String, index=True)
    company: Mapped[str] = mapped_column(String, index=True)
    location: Mapped[str | None] = mapped_column(String, index=True)
    status: Mapped[JobStatus] = mapped_column(SqlEnum(JobStatus), default=JobStatus.applied, index=True)
    source: Mapped[JobSource | None] = mapped_column(SqlEnum(JobSource), index=True)
    date_applied: Mapped[date | None] = mapped_column(Date, index=True)
    job_url: Mapped[str | None] = mapped_column(String, index=True)
    notes: Mapped[str | None] = mapped_column(Text)
