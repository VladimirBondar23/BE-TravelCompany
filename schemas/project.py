"""
Project request/response schemas and serializers.
"""
from datetime import date
from typing import List, Optional, Union

from pydantic import BaseModel, Field

from models import Project
from schemas.place import PlaceOut


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_date: Optional[date] = None


class ProjectCreate(ProjectBase):
    place_ids: Optional[List[Union[int, str]]] = Field(
        default=None, description="Optional list of external place IDs"
    )


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_date: Optional[date] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]
    places_count: int
    completed: bool

    class Config:
        from_attributes = True


class ProjectDetailOut(ProjectOut):
    places: List[PlaceOut]


class ProjectListOut(BaseModel):
    """Paginated project list."""
    items: List[ProjectOut]
    total: int


class ProjectListOut(BaseModel):
    """Paginated project list response."""
    items: List[ProjectOut]
    total: int


def _places_sorted_newest_first(places: list) -> list:
    return sorted(places or [], key=lambda p: p.id, reverse=True)


def project_to_out(project: Project) -> ProjectOut:
    places = project.places or []
    places_count = len(places)
    completed = places_count > 0 and all(p.visited for p in places)
    return ProjectOut(
        id=project.id,
        name=project.name,
        description=project.description,
        start_date=project.start_date,
        places_count=places_count,
        completed=completed,
    )


def project_to_detail_out(project: Project) -> ProjectDetailOut:
    base = project_to_out(project)
    ordered = _places_sorted_newest_first(project.places)
    return ProjectDetailOut(
        **base.model_dump(),
        places=[
            PlaceOut(
                id=p.id,
                project_id=p.project_id,
                external_id=p.external_id,
                title=getattr(p, "title", None),
                notes=p.notes,
                visited=p.visited,
            )
            for p in ordered
        ],
    )


def place_to_out(place) -> PlaceOut:
    return PlaceOut(
        id=place.id,
        project_id=place.project_id,
        external_id=place.external_id,
        title=getattr(place, "title", None),
        notes=place.notes,
        visited=place.visited,
    )
