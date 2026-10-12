from pydantic import BaseModel, ConfigDict

from app.rendering.contracts import ParameterType, ParameterValue


class ParameterSchema(BaseModel):
    type: ParameterType
    default: ParameterValue
    minimum: int | float | None = None
    maximum: int | float | None = None
    options: tuple[str, ...] = ()
    label: str
    description: str | None = None


class PresetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    description: str | None
    renderer_id: str
    renderer_version: int
    parameters: dict[str, ParameterSchema]
    revision: int
