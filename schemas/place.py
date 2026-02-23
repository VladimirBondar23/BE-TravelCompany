"""
Place request/response schemas.
"""
from typing import List, Optional, Union

from pydantic import BaseModel, Field


class PlaceBase(BaseModel):
    external_id: Union[int, str] = Field(..., description="Art Institute external ID")
    notes: Optional[str] = Field(None, max_length=2000)


class PlaceCreate(PlaceBase):
    pass


class PlaceUpdate(BaseModel):
    notes: Optional[str] = Field(None, max_length=2000)
    visited: Optional[bool] = None


class PlaceOut(BaseModel):
    id: int
    project_id: int
    external_id: str
    title: Optional[str] = None
    notes: Optional[str]
    visited: bool

    class Config:
        from_attributes = True


class PlaceListOut(BaseModel):
    """Paginated place list."""
    items: List[PlaceOut]
    total: int
