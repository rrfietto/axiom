from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import Artwork
from app.db.session import get_db
from app.schemas.artwork import ArtworkResponse
from app.services.artwork_service import ArtworkNotFoundError, ArtworkService

router = APIRouter(prefix="/artworks", tags=["artworks"])

DatabaseSession = Annotated[Session, Depends(get_db)]


def get_artwork_service(session: DatabaseSession) -> ArtworkService:
    return ArtworkService(session, get_settings().artwork_directory)


ArtworkServiceDependency = Annotated[ArtworkService, Depends(get_artwork_service)]


def artwork_response(artwork: Artwork) -> ArtworkResponse:
    return ArtworkResponse(
        id=artwork.id,
        preset_slug=artwork.preset_slug,
        preset_name=artwork.preset_name,
        preset_revision=artwork.preset_revision,
        renderer_id=artwork.renderer_id,
        renderer_version=artwork.renderer_version,
        parameters=artwork.parameters,
        seed=artwork.seed,
        width=artwork.width,
        height=artwork.height,
        image_url=f"/api/artworks/{artwork.id}/image",
        created_at=artwork.created_at,
    )


def not_found(error: ArtworkNotFoundError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@router.get("", response_model=list[ArtworkResponse])
def list_artworks(
    service: ArtworkServiceDependency,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[ArtworkResponse]:
    return [artwork_response(item) for item in service.list(offset=offset, limit=limit)]


@router.get("/{artwork_id}", response_model=ArtworkResponse)
def get_artwork(
    artwork_id: int,
    service: ArtworkServiceDependency,
) -> ArtworkResponse:
    try:
        return artwork_response(service.get(artwork_id))
    except ArtworkNotFoundError as error:
        raise not_found(error) from error


@router.get("/{artwork_id}/image", response_class=FileResponse)
def get_artwork_image(
    artwork_id: int,
    service: ArtworkServiceDependency,
) -> FileResponse:
    try:
        path = service.image_file(artwork_id)
    except ArtworkNotFoundError as error:
        raise not_found(error) from error
    return FileResponse(
        path,
        media_type="image/png",
        filename=f"artwork-{artwork_id}.png",
    )


@router.delete("/{artwork_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_artwork(
    artwork_id: int,
    service: ArtworkServiceDependency,
) -> Response:
    try:
        service.delete(artwork_id)
    except ArtworkNotFoundError as error:
        raise not_found(error) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
