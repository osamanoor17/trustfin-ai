"""Health check schema definition."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Schema for /health response payload."""

    status: str
    project: str
    version: str
