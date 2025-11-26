"""
Common schemas for API responses.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(..., description="Overall service status")
    timestamp: str = Field(..., description="Current timestamp in ISO format")
    database: str = Field(..., description="Database connection status")
    cache: str = Field(..., description="Redis cache connection status")
    queue: str = Field(..., description="Message queue connection status")
    version: Optional[str] = Field(None, description="Service version")
    environment: Optional[str] = Field(None, description="Environment (development/production)")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "timestamp": "2025-11-25T18:30:00Z",
                "database": "connected",
                "cache": "connected",
                "queue": "connected",
                "version": "1.0.0",
                "environment": "development"
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Not Found",
                "detail": "Resource not found",
                "timestamp": "2025-11-25T18:30:00Z"
            }
        }


class SuccessResponse(BaseModel):
    """Success response schema."""
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {}
            }
        }

