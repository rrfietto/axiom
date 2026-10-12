from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Artwork
from app.services.render_service import RenderResult


class ArtworkNotFoundError(Exception):
    pass


class ArtworkStorageError(Exception):
    pass


class ArtworkService:
    def __init__(self, session: Session, storage_root: Path) -> None:
        self._session = session
        self._storage_root = storage_root

    def save(self, result: RenderResult) -> Artwork:
        now = datetime.now(UTC)
        relative_path = Path(str(now.year), f"{now.month:02d}", f"{uuid4()}.png")
        destination = self._storage_root / relative_path
        temporary = destination.with_suffix(".tmp")
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            result.image.save(temporary, format="PNG")
            temporary.replace(destination)
            artwork = Artwork(
                preset_id=result.preset.preset.id,
                preset_slug=result.preset.preset.slug,
                preset_name=result.preset.preset.name,
                preset_revision=result.preset.preset.revision,
                renderer_id=result.preset.renderer.id,
                renderer_version=result.preset.renderer.version,
                parameters=dict(result.parameters),
                seed=result.seed,
                width=result.image.width,
                height=result.image.height,
                image_path=relative_path.as_posix(),
                created_at=now,
            )
            self._session.add(artwork)
            self._session.commit()
            self._session.refresh(artwork)
            return artwork
        except Exception as error:
            self._session.rollback()
            temporary.unlink(missing_ok=True)
            destination.unlink(missing_ok=True)
            raise ArtworkStorageError("Could not persist artwork") from error

    def list(self, *, offset: int, limit: int) -> list[Artwork]:
        statement = (
            select(Artwork)
            .order_by(Artwork.created_at.desc(), Artwork.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self._session.scalars(statement))

    def get(self, artwork_id: int) -> Artwork:
        artwork = self._session.get(Artwork, artwork_id)
        if artwork is None:
            raise ArtworkNotFoundError(f"Artwork {artwork_id} was not found")
        return artwork

    def image_file(self, artwork_id: int) -> Path:
        artwork = self.get(artwork_id)
        path = self._storage_root / artwork.image_path
        if not path.is_file():
            raise ArtworkNotFoundError(f"Image for artwork {artwork_id} was not found")
        return path

    def delete(self, artwork_id: int) -> None:
        artwork = self.get(artwork_id)
        path = self._storage_root / artwork.image_path
        self._session.delete(artwork)
        self._session.commit()
        path.unlink(missing_ok=True)
