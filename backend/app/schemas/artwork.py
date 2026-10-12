from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.rendering.contracts import ParameterValue


class ArtworkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    preset_slug: str
    preset_name: str
    preset_revision: int
    renderer_id: str
    renderer_version: int
    parameters: dict[str, ParameterValue]
    seed: int
    width: int
    height: int
    image_url: str
    created_at: datetime
