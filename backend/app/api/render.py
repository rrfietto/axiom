from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.rendering.engine import RenderingEngine
from app.rendering.exceptions import InvalidDimensionsError, ParameterValidationError
from app.rendering.registry import renderer_registry
from app.schemas.render import RenderRequest
from app.services.preset_service import PresetNotFoundError, PresetService
from app.services.render_service import RenderService

router = APIRouter(tags=["render"])

DatabaseSession = Annotated[Session, Depends(get_db)]


def get_render_service(session: DatabaseSession) -> RenderService:
    return RenderService(
        PresetService(session, renderer_registry),
        RenderingEngine(renderer_registry),
    )


RenderServiceDependency = Annotated[RenderService, Depends(get_render_service)]


@router.post(
    "/render",
    response_class=StreamingResponse,
    responses={200: {"content": {"image/png": {}}}},
)
def render_art(
    request: RenderRequest,
    service: RenderServiceDependency,
) -> StreamingResponse:
    try:
        image = service.render(
            request.preset_slug,
            width=request.width,
            height=request.height,
            seed=request.seed,
            parameters=request.parameters,
        )
    except PresetNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except (InvalidDimensionsError, ParameterValidationError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error

    output = BytesIO()
    image.save(output, format="PNG")
    _ = output.seek(0)
    return StreamingResponse(
        output,
        media_type="image/png",
        headers={
            "Content-Disposition": 'inline; filename="axiom.png"',
            "X-Axiom-Preset": request.preset_slug,
            "X-Axiom-Seed": str(request.seed),
        },
    )
