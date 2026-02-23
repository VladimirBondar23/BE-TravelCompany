"""
Project API controller (business logic for project endpoints).
"""
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import Integer, func, or_, select
from sqlalchemy.orm import Session

from config import MAX_PLACES_PER_PROJECT
from models import Project, ProjectPlace
from schemas import (
    ProjectCreate,
    ProjectDetailOut,
    ProjectListOut,
    ProjectOut,
    ProjectUpdate,
    project_to_detail_out,
    project_to_out,
)
from services import fetch_artwork_title


async def create_project(payload: ProjectCreate, db: Session) -> ProjectOut:
    place_ids = payload.place_ids or []
    if len(place_ids) > MAX_PLACES_PER_PROJECT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_PLACES_PER_PROJECT} places per project",
        )

    unique_ids: List[str] = []
    for pid in place_ids:
        eid = str(pid)
        if eid not in unique_ids:
            unique_ids.append(eid)

    id_to_title: dict[str, str | None] = {}
    for eid in unique_ids:
        id_to_title[eid] = await fetch_artwork_title(eid)

    project = Project(
        name=payload.name.strip(),
        description=payload.description.strip() if payload.description else None,
        start_date=payload.start_date,
    )
    db.add(project)
    db.flush()

    for eid in unique_ids:
        db.add(
            ProjectPlace(
                project_id=project.id,
                external_id=eid,
                title=id_to_title.get(eid),
                visited=False,
            )
        )

    db.commit()
    db.refresh(project)
    return project_to_out(project)


def list_projects(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    search: str | None = None,
    completed: bool | None = None,
) -> ProjectListOut:
    q = db.query(Project).order_by(Project.id.desc())
    if search and search.strip():
        term = f"%{search.strip()}%"
        q = q.filter(
            or_(
                Project.name.ilike(term),
                (Project.description.isnot(None) & Project.description.ilike(term)),
            )
        )
    if completed is not None:
        # Completed = at least one place and all places visited.
        completed_sub = (
            db.query(ProjectPlace.project_id)
            .group_by(ProjectPlace.project_id)
            .having(
                func.count(ProjectPlace.id) > 0,
                func.count(ProjectPlace.id) == func.sum(func.cast(ProjectPlace.visited, Integer)),
            )
        ).subquery()
        if completed:
            q = q.filter(Project.id.in_(select(completed_sub.c.project_id)))
        else:
            # Not completed: no places or at least one place not visited
            q = q.filter(~Project.id.in_(select(completed_sub.c.project_id)))
    total = q.count()
    projects = q.offset(skip).limit(limit).all()
    return ProjectListOut(items=[project_to_out(p) for p in projects], total=total)


def get_project(project_id: int, db: Session) -> ProjectDetailOut:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_to_detail_out(project)


def update_project(project_id: int, payload: ProjectUpdate, db: Session) -> ProjectOut:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if payload.name is not None:
        project.name = payload.name.strip()
    if payload.description is not None:
        project.description = payload.description.strip() or None
    if payload.start_date is not None:
        project.start_date = payload.start_date

    db.commit()
    db.refresh(project)
    return project_to_out(project)


def delete_project(project_id: int, db: Session) -> None:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    any_visited = (
        db.query(ProjectPlace)
        .filter(ProjectPlace.project_id == project_id, ProjectPlace.visited.is_(True))
        .first()
        is not None
    )
    if any_visited:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete project with visited places",
        )

    db.delete(project)
    db.commit()
