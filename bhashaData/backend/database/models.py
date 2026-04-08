from datetime import datetime, timezone
import json
from uuid import uuid4

from sqlalchemy import DateTime, Integer, String, Text, select, ForeignKey, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True)
    request_payload: Mapped[str] = mapped_column(Text)
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_dir: Mapped[str | None] = mapped_column(String(255), nullable=True)
    exported_formats: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=2)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class DatasetArtifact(Base):
    __tablename__ = "dataset_artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(64), index=True)
    format: Mapped[str] = mapped_column(String(32))
    path: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


def create_job(db, job_id, request_payload, estimated_minutes, email, user_id=None) -> Job:
    job = Job(
        id=job_id,
        user_id=user_id,
        status="queued",
        request_payload=json.dumps(request_payload, ensure_ascii=False),
        estimated_minutes=estimated_minutes,
        email=email,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def update_job_status(
    db,
    job_id,
    status,
    result_summary=None,
    output_dir=None,
    exported_formats=None,
    error_message=None,
) -> Job:
    job = get_job(db, job_id)
    if job is None:
        raise ValueError(f"Job not found: {job_id}")

    job.status = status
    job.result_summary = None if result_summary is None else json.dumps(result_summary, ensure_ascii=False)
    job.output_dir = output_dir
    job.exported_formats = None if exported_formats is None else json.dumps(exported_formats, ensure_ascii=False)
    job.error_message = error_message
    job.updated_at = datetime.now(timezone.utc)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job(db, job_id) -> Job | None:
    return db.execute(select(Job).where(Job.id == job_id)).scalar_one_or_none()


# User functions
def create_user(db, email: str, hashed_password: str, full_name: str | None = None) -> User:
    """Create a new user."""
    user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db, email: str) -> User | None:
    """Get user by email."""
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def get_user_by_id(db, user_id: str) -> User | None:
    """Get user by user ID."""
    return db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()


def get_jobs_by_user(db, user_id: str, limit: int = 20) -> list[Job]:
    """Get all jobs for a user."""
    return (
        db.execute(
            select(Job)
            .where(Job.user_id == user_id)
            .order_by(Job.created_at.desc())
            .limit(limit)
        )
        .scalars()
        .all()
    )

