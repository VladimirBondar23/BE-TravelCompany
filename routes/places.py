"""
Place API routes (nested under projects).
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from auth import verify_basic_auth
from controllers import place_controller
from database import get_db
from schemas import PlaceCreate, PlaceListOut, PlaceOut, PlaceUpdate

router = APIRouter(prefix="/projects/{project_id}/places", tags=["places"])


@router.get(
    "",
    response_model=PlaceListOut,
    summary="List places for a project (paginated)",
)
def list_places(
    project_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(verify_basic_auth),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    return place_controller.list_places(project_id, db, skip=skip, limit=limit)


@router.post(
    "",
    response_model=PlaceOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add a place to an existing project",
)
async def add_place(
    project_id: int,
    payload: PlaceCreate,
    db: Session = Depends(get_db),
    _: None = Depends(verify_basic_auth),
):
    return await place_controller.add_place(project_id, payload, db)


@router.get(
    "/{place_id}",
    response_model=PlaceOut,
    summary="Get a single place within a project",
)
def get_place(
    project_id: int,
    place_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(verify_basic_auth),
):
    return place_controller.get_place(project_id, place_id, db)


@router.patch(
    "/{place_id}",
    response_model=PlaceOut,
    summary="Update a place within a project (notes / visited)",
)
def update_place(
    project_id: int,
    place_id: int,
    payload: PlaceUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(verify_basic_auth),
):
    return place_controller.update_place(project_id, place_id, payload, db)
