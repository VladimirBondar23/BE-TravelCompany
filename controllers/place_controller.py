"""
Place API controller (business logic for place endpoints).
"""
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from config import MAX_PLACES_PER_PROJECT
from models import Project, ProjectPlace
from schemas import PlaceCreate, PlaceListOut, PlaceOut, PlaceUpdate, place_to_out
from schemas.project import _places_sorted_newest_first
from services import fetch_artwork_title


def list_places(
    project_id: int,
    db: Session,
    skip: int = 0,
    limit: int = 20,
) -> PlaceListOut:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    ordered = _places_sorted_newest_first(project.places)
    total = len(ordered)
    page = ordered[skip : skip + limit]
    return PlaceListOut(items=[place_to_out(p) for p in page], total=total)


async def add_place(project_id: int, payload: PlaceCreate, db: Session) -> PlaceOut:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    current_count = (
        db.query(ProjectPlace)
        .filter(ProjectPlace.project_id == project_id)
        .count()
    )
    if current_count >= MAX_PLACES_PER_PROJECT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_PLACES_PER_PROJECT} places per project",
        )

    external_id_str = str(payload.external_id)
    existing = (
        db.query(ProjectPlace)
        .filter(
            ProjectPlace.project_id == project_id,
            ProjectPlace.external_id == external_id_str,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This place is already added to the project",
        )

    title = await fetch_artwork_title(external_id_str)
    place = ProjectPlace(
        project_id=project_id,
        external_id=external_id_str,
        title=title,
        notes=payload.notes,
        visited=False,
    )
    db.add(place)
    db.commit()
    db.refresh(place)
    return place_to_out(place)


def get_place(project_id: int, place_id: int, db: Session) -> PlaceOut:
    place = (
        db.query(ProjectPlace)
        .filter(
            ProjectPlace.project_id == project_id,
            ProjectPlace.id == place_id,
        )
        .first()
    )
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place_to_out(place)


def update_place(project_id: int, place_id: int, payload: PlaceUpdate, db: Session) -> PlaceOut:
    place = (
        db.query(ProjectPlace)
        .filter(
            ProjectPlace.project_id == project_id,
            ProjectPlace.id == place_id,
        )
        .first()
    )
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")

    if payload.notes is not None:
        place.notes = payload.notes.strip() or None
    if payload.visited is not None:
        place.visited = payload.visited

    db.commit()
    db.refresh(place)
    return place_to_out(place)