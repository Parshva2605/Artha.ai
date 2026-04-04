from uuid import uuid4

from fastapi import APIRouter

from api.models import GenerateDatasetRequest, GenerateDatasetResponse, HealthResponse

router = APIRouter()


@router.post("/generate-dataset", response_model=GenerateDatasetResponse)
def generate_dataset(_: GenerateDatasetRequest) -> GenerateDatasetResponse:
    return GenerateDatasetResponse(job_id=str(uuid4()), estimated_minutes=8)


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", version="1.0")
