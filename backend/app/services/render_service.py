from dataclasses import dataclass

from PIL import Image

from app.rendering.contracts import ParameterDefinition, ParameterValue
from app.rendering.engine import RenderingEngine
from app.rendering.exceptions import ParameterValidationError
from app.services.preset_service import PresetService, ResolvedPreset


@dataclass(frozen=True)
class RenderResult:
    image: Image.Image
    preset: ResolvedPreset
    parameters: dict[str, ParameterValue]
    seed: int


class RenderService:
    def __init__(
        self,
        preset_service: PresetService,
        engine: RenderingEngine,
    ) -> None:
        self._preset_service: PresetService = preset_service
        self._engine: RenderingEngine = engine

    def render(
        self,
        preset_slug: str,
        *,
        width: int,
        height: int,
        seed: int,
        parameters: dict[str, ParameterValue],
    ) -> RenderResult:
        preset = self._preset_service.resolve_enabled(preset_slug)
        unknown = parameters.keys() - preset.parameters.keys()
        if unknown:
            names = ", ".join(sorted(unknown))
            raise ParameterValidationError(f"Unknown parameters: {names}")

        effective_parameters: dict[str, ParameterValue] = {}
        for name, schema in preset.parameters.items():
            definition = ParameterDefinition(
                type=schema.type,
                default=schema.default,
                minimum=schema.minimum,
                maximum=schema.maximum,
                options=schema.options,
            )
            effective_parameters[name] = definition.validate(
                name,
                parameters.get(name, schema.default),
            )

        image = self._engine.render(
            preset.renderer.id,
            width=width,
            height=height,
            seed=seed,
            parameters=effective_parameters,
        )
        return RenderResult(
            image=image,
            preset=preset,
            parameters=effective_parameters.copy(),
            seed=seed,
        )
