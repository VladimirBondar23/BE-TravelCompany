"""
Common query/response schemas (pagination, filtering).
"""
from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query params for paginated list endpoints."""
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=20, ge=1, le=100, description="Max items to return")


class ProjectListParams(PaginationParams):
    """Query params for listing projects (pagination + filters)."""
    search: str | None = Field(default=None, max_length=200, description="Filter by name or description (case-insensitive substring)")
    completed: bool | None = Field(default=None, description="Filter by completed: true | false | omit for all")


class ListResponse(BaseModel, Generic[T]):
    """Paginated list response."""
    items: List[T]
    total: int
