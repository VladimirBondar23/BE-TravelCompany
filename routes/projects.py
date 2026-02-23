"""
Project API routes.
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from auth import verify_basic_auth
from controllers import project_controller
from database import get_db
from schemas import (
    ProjectCreate,
    ProjectDetailOut,
    ProjectListOut,
    ProjectOut,
    ProjectUpdate,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "",
    response_model=ProjectOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a travel project (optionally with places)",
)
async def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    _: None = Depends(verify_basic_auth),
):
    return await project_controller.create_project(payload, db)


@router.get(
    "",
    response_model=ProjectListOut,
    summary="List travel projects (paginated, optional search and completed filter)",
)
def list_projects(
    db: Session = Depends(get_db),
    _: None = Depends(verify_basic_auth),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=200),
    completed: bool | None = Query(None),
):
    return project_controller.list_projects(db, skip=skip, limit=limit, search=search, completed=completed)


@router.get(
    "/{project_id}",
    response_model=ProjectDetailOut,
    summary="Get a single project with its places",
)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(verify_basic_auth),
):
    return project_controller.get_project(project_id, db)


@router.put(
    "/{project_id}",
    response_model=ProjectOut,
    summary="Update project information",
)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(verify_basic_auth),
):
    return project_controller.update_project(project_id, payload, db)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project (only if no visited places)",
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(verify_basic_auth),
):
    project_controller.delete_project(project_id, db)
