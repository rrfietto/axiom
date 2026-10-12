from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.rendering.registry import renderer_registry
from app.schemas.preset import PresetResponse
from app.services.preset_service import PresetNotFoundError, PresetService

router = APIRouter(prefix="/presets", tags=["presets"])

DatabaseSession = Annotated[Session, Depends(get_db)]


def get_preset_service(session: DatabaseSession) -> PresetService:
    return PresetService(session, renderer_registry)


PresetServiceDependency = Annotated[PresetService, Depends(get_preset_service)]


@router.get("", response_model=list[PresetResponse])
def list_presets(service: PresetServiceDependency) -> list[PresetResponse]:
    return service.list_enabled()


@router.get("/{slug}", response_model=PresetResponse)
def get_preset(
    slug: str,
    service: PresetServiceDependency,
) -> PresetResponse:
    try:
        return service.get_enabled(slug)
    except PresetNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
