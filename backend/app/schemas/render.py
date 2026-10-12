from pydantic import BaseModel, ConfigDict, Field

from app.rendering.contracts import ParameterValue


class RenderRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    preset_slug: str = Field(min_length=1, max_length=100)
    width: int = Field(default=1024, ge=1)
    height: int = Field(default=1024, ge=1)
    seed: int = Field(default=0, ge=0, lt=2**32)
    parameters: dict[str, ParameterValue] = Field(default_factory=dict)
