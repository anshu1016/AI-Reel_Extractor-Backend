"""
Common Pydantic schemas used across the application.
"""

from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional, Any
from datetime import datetime


# Generic type for paginated responses
T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response model.
    
    Example:
        PaginatedResponse[VideoResponse](
            items=[video1, video2],
            total=100,
            page=1,
            page_size=20
        )
    """
    items: List[T]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool
    
    @classmethod
    def create(cls, items: List[T], total: int, page: int, page_size: int):
        """Helper to create paginated response with computed fields."""
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_next=page * page_size < total,
            has_prev=page > 1
        )


class SuccessResponse(BaseModel):
    """Standard success response."""
    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error: str
    message: str
    code: Optional[str] = None
    details: Optional[dict] = None


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str


class StatusResponse(BaseModel):
    """Status response with additional info."""
    status: str
    message: Optional[str] = None
    timestamp: datetime = datetime.utcnow()


class HealthResponse(BaseModel):
    """Health check response."""
    status: str  # healthy, unhealthy, degraded
    version: str
    database: dict
    timestamp: datetime = datetime.utcnow()


class BulkOperationResponse(BaseModel):
    """Response for bulk operations."""
    success_count: int
    failure_count: int
    total: int
    errors: Optional[List[dict]] = None


# Validation error detail
class ValidationError(BaseModel):
    """Validation error detail."""
    field: str
    message: str
    code: str