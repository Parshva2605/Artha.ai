from pydantic import BaseModel, EmailStr, Field


class GenerateDatasetRequest(BaseModel):
    languages: list[str]
    domain: str
    label_type: str
    quantity_per_language: int = Field(ge=100, le=5000)
    export_formats: list[str]
    email: EmailStr | None = None


class GenerateDatasetResponse(BaseModel):
    job_id: str
    estimated_minutes: int


class HealthResponse(BaseModel):
    status: str
    version: str
