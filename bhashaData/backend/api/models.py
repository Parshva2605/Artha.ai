from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.config.languages import is_supported_language


SUPPORTED_EXPORT_FORMATS = {"csv", "json", "excel", "parquet", "huggingface"}
SUPPORTED_DOMAINS = {"app_reviews", "social_media", "news", "mixed"}
SUPPORTED_LABEL_TYPES = {"sentiment", "topic", "ner", "all", "custom"}


class GenerateDatasetRequest(BaseModel):
    languages: list[str] = Field(min_length=1, max_length=5)
    domain: str
    label_type: str
    quantity_per_language: int = Field(
        default=100,
        ge=100,
        le=300,
        description="Number of rows per language (demo limit: 300)",
    )
    export_formats: list[str] = Field(min_length=1)
    email: str | None = None
    custom_labels: list[str] | None = None

    @field_validator("languages")
    @classmethod
    def validate_languages(cls, languages: list[str]) -> list[str]:
        if len(set(languages)) != len(languages):
            raise ValueError("languages must not contain duplicates")
        for language_code in languages:
            if not is_supported_language(language_code):
                raise ValueError(f"Unsupported language code: {language_code}")
        return languages

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, domain: str) -> str:
        if domain not in SUPPORTED_DOMAINS:
            raise ValueError(f"Unsupported domain: {domain}")
        return domain

    @field_validator("label_type")
    @classmethod
    def validate_label_type(cls, label_type: str) -> str:
        if label_type not in SUPPORTED_LABEL_TYPES:
            raise ValueError(f"Unsupported label_type: {label_type}")
        return label_type

    @field_validator("export_formats")
    @classmethod
    def validate_export_formats(cls, export_formats: list[str]) -> list[str]:
        if not export_formats:
            raise ValueError("At least one export format must be selected")
        if len(set(export_formats)) != len(export_formats):
            raise ValueError("export_formats must not contain duplicates")
        for format_name in export_formats:
            if format_name not in SUPPORTED_EXPORT_FORMATS:
                raise ValueError(f"Unsupported export format: {format_name}")
        return export_formats

    @field_validator("email")
    @classmethod
    def validate_email(cls, email: str | None) -> str | None:
        if email is None:
            return None
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise ValueError("Invalid email format")
        return email

    @field_validator("custom_labels", mode="after")
    @classmethod
    def validate_custom_labels(cls, v: list[str] | None, info) -> list[str] | None:
        label_type = info.data.get("label_type")
        if label_type == "custom":
            if not v or len(v) < 2:
                raise ValueError("Custom label type requires at least 2 labels")
            if len(v) > 10:
                raise ValueError("Maximum 10 custom labels allowed")
            for label in v:
                label_stripped = label.strip()
                if not label_stripped:
                    raise ValueError("Label names cannot be empty")
                if len(label_stripped) > 30:
                    raise ValueError(f"Label '{label_stripped}' exceeds 30 character limit")
        return v


class GenerateDatasetResponse(BaseModel):
    job_id: str
    estimated_minutes: int
    message: str

class UploadPreviewResponse(BaseModel):
    upload_id: str
    filename: str
    total_rows: int
    column_names: list[str]
    detected_text_column: str
    preview_rows: list[dict]


class HealthResponse(BaseModel):
    status: str
    version: str
    redis_connected: bool
    database_connected: bool


class JobStatusResponse(BaseModel):
    job_id: str
    status: Literal["queued", "scraping", "cleaning", "labeling", "quality_check", "exporting", "complete", "failed", "cancelled"]
    progress_percent: int
    current_step: str
    per_language_status: dict[str, dict[str, Any]]
    eta_seconds: int | None
    error_message: str | None
    created_at: str
    updated_at: str


class BalanceResultResponse(BaseModel):
    is_balanced: bool
    dominant_label: str | None
    dominant_percentage: float
    warning_message: str | None


# Authentication models
class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)
    full_name: str | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, email: str) -> str:
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise ValueError("Invalid email format")
        return email


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    user_id: str
    email: str
    full_name: str | None
    access_token: str


class UserResponse(BaseModel):
    user_id: str
    email: str
    full_name: str | None
    is_active: bool


class JobResponse(BaseModel):
    job_id: str
    status: str
    created_at: str
    updated_at: str



class BenchmarkComparisonResponse(BaseModel):
    english_score: float | None
    other_scores: dict[str, float]
    differences: dict[str, float]
    benchmark_note: str


class QualityReportResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    job_id: str
    overall_quality_score: float
    per_language_quality: dict[str, float]
    label_distribution: dict[str, int]
    per_language_distribution: dict[str, dict[str, int]]
    balance_result: BalanceResultResponse
    benchmark_comparison: BenchmarkComparisonResponse
    total_labeled: int
    total_needs_review: int
    total_rejected_low_confidence: int
    claude_count: int
    openai_count: int
    openrouter_count: int
    ollama_count: int
    needs_review_count: int
    shortfall_warnings: list[str]
    low_quality_warning: str | None
    is_low_quality: bool
    generated_at: str
