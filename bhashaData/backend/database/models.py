from datetime import datetime, timezone
import json

from sqlalchemy import DateTime, Integer, String, Text, select
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.db import Base, engine


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
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


Base.metadata.create_all(bind=engine)


def create_job(db, job_id, request_payload, estimated_minutes, email) -> Job:
    job = Job(
        id=job_id,
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
