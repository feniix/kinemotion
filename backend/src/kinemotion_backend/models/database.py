"""Database models for analysis sessions and coach feedback."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AnalysisSessionCreate(BaseModel):
    """Model for creating a new analysis session."""

    jump_type: str = Field(..., description="Type of jump: 'cmj' or 'drop_jump'")
    quality_preset: str = Field(
        ..., description="Analysis quality: 'fast', 'balanced', or 'accurate'"
    )
    original_video_url: str | None = Field(None, description="R2 URL for original video")
    debug_video_url: str | None = Field(None, description="R2 URL for debug video")
    results_json_url: str | None = Field(None, description="R2 URL for results JSON")
    analysis_data: dict[str, Any] = Field(..., description="Analysis results as JSON")
    processing_time_s: float | None = Field(None, description="Processing time in seconds")
    upload_id: str | None = Field(None, description="Upload ID from analysis system")

    @field_validator("jump_type")
    @classmethod
    def validate_jump_type(cls, v: str) -> str:
        if v not in ["cmj", "drop_jump"]:
            raise ValueError("jump_type must be 'cmj' or 'drop_jump'")
        return v

    @field_validator("quality_preset")
    @classmethod
    def validate_quality_preset(cls, v: str) -> str:
        if v not in ["fast", "balanced", "accurate"]:
            raise ValueError("quality_preset must be 'fast', 'balanced', or 'accurate'")
        return v


class AnalysisSessionResponse(BaseModel):
    """Model for analysis session response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: str
    jump_type: str
    quality_preset: str
    original_video_url: str | None
    debug_video_url: str | None
    results_json_url: str | None
    analysis_data: dict[str, Any]
    processing_time_s: float | None
    upload_id: str | None
    created_at: datetime
    updated_at: datetime


class CoachFeedbackCreate(BaseModel):
    """Model for creating coach feedback."""

    analysis_session_id: UUID = Field(..., description="ID of the analysis session")
    notes: str | None = Field(None, description="Coach notes about the analysis")
    rating: int | None = Field(None, ge=1, le=5, description="Rating from 1-5")
    tags: list[str] = Field(default_factory=list, description="Tags for categorizing feedback")

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int | None) -> int | None:
        if v is not None and (v < 1 or v > 5):
            raise ValueError("rating must be between 1 and 5")
        return v


class CoachFeedbackResponse(BaseModel):
    """Model for coach feedback response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    analysis_session_id: UUID
    coach_user_id: str
    notes: str | None
    rating: int | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime


class AnalysisSessionWithFeedback(AnalysisSessionResponse):
    """Analysis session with associated feedback."""

    feedback: list[CoachFeedbackResponse] = Field(default_factory=list)


class DatabaseError(BaseModel):
    """Model for database errors."""

    error: str = Field(..., description="Error message")
    code: str | None = Field(None, description="Error code")
    details: dict[str, Any] | None = Field(None, description="Additional error details")
