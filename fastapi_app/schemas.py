"""
Pydantic schemas for request/response validation.
Provides type-safe API contracts with automatic validation and documentation.
"""

from pydantic import BaseModel, Field, field_validator, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime


class PopulateRagRequest(BaseModel):
    """Request model for RAG population."""

    theme: str = Field(..., min_length=1, description="Theme name")
    examples: List[Dict[str, Any]] = Field(
        default=[], description="Examples to populate")

    class Config:
        json_schema_extra = {
            "example": {
                "theme": "python_basics",
                "examples": [
                    {"id": 1, "code": "print('Hello')"},
                    {"id": 2, "code": "x = [1, 2, 3]"}
                ]
            }
        }


class DeleteRagRequest(BaseModel):
    """Request model for RAG deletion."""

    task_id: int = Field(..., gt=0, description="Task ID")
    theme: str = Field(..., min_length=1, description="Theme name")
    prog_lang: str = Field(..., min_length=1,
                           description="Programming language")

    @field_validator('prog_lang')
    @classmethod
    def validate_prog_lang(cls, v: str) -> str:
        allowed = {'python', 'java', 'javascript', 'cpp', 'c'}
        if v.lower() not in allowed:
            raise ValueError(f"Programming language must be one of {allowed}")
        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 1,
                "theme": "python_basics",
                "prog_lang": "python"
            }
        }


class EvaluateRequest(BaseModel):
    """Request model for code evaluation."""

    task_id: int = Field(..., gt=0, description="Task ID")
    theme: str = Field(..., min_length=1, description="Theme name")
    prog_lang: str = Field(..., min_length=1,
                           description="Programming language")
    model: str = Field(..., min_length=1,
                       description="Model to use for evaluation")
    agent: str = Field(..., min_length=1, description="Agent name")
    api_key: str = Field(..., description="API key for authentication")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 1,
                "theme": "python_basics",
                "prog_lang": "python",
                "model": "gpt-4",
                "agent": "evaluator-1",
                "api_key": "sk-..."
            }
        }


class SuccessResponse(BaseModel):
    """Generic success response."""

    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully",
                "data": {"id": 1},
                "timestamp": "2024-01-15T10:30:00"
            }
        }


class ErrorResponse(BaseModel):
    """Generic error response."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid input provided",
                "details": {"field": "theme", "reason": "Required field"},
                "timestamp": "2024-01-15T10:30:00"
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Check timestamp")
    services: Optional[Dict[str, Dict[str, Any]]] = Field(
        None, description="Service health status")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2024-01-15T10:30:00",
                "services": {
                    "database": {"healthy": True},
                    "cache": {"healthy": True}
                }
            }
        }
