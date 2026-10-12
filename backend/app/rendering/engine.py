from collections.abc import Mapping
from types import MappingProxyType

from PIL import Image

from app.rendering.contracts import (
    ParameterValue,
    RenderContext,
    RendererDefinition,
)
from app.rendering.exceptions import (
    InvalidDimensionsError,
    InvalidRendererOutputError,
    ParameterValidationError,
)
from app.rendering.registry import RendererRegistry


class RenderingEngine:
    def __init__(self, registry: RendererRegistry) -> None:
        self._registry: RendererRegistry = registry

    def render(
        self,
        renderer_id: str,
        *,
        width: int,
        height: int,
        seed: int,
        parameters: Mapping[str, object] | None = None,
    ) -> Image.Image:
        renderer = self._registry.get(renderer_id)
        self._validate_dimensions(renderer, width, height)
        if isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed < 2**32:
            raise ParameterValidationError(
                "seed must be an integer between 0 and 4294967295"
            )

        supplied = parameters or {}
        unknown = supplied.keys() - renderer.parameters.keys()
        if unknown:
            names = ", ".join(sorted(unknown))
            raise ParameterValidationError(f"Unknown parameters: {names}")

        normalized: dict[str, ParameterValue] = {}
        for name, definition in renderer.parameters.items():
            normalized[name] = definition.validate(
                name, supplied.get(name, definition.default)
            )

        context = RenderContext(
            width=width,
            height=height,
            seed=seed,
            parameters=MappingProxyType(normalized),
        )
        image = renderer.render(context)
        if not isinstance(image, Image.Image):
            raise InvalidRendererOutputError(
                f"Renderer '{renderer.id}' did not return a Pillow image"
            )
        if image.size != (width, height):
            raise InvalidRendererOutputError(
                f"Renderer '{renderer.id}' returned {image.size}, expected "
                f"{(width, height)}"
            )
        return image

    @staticmethod
    def _validate_dimensions(
        renderer: RendererDefinition, width: int, height: int
    ) -> None:
        if (
            isinstance(width, bool)
            or isinstance(height, bool)
            or not isinstance(width, int)
            or not isinstance(height, int)
            or width < 1
            or height < 1
        ):
            raise InvalidDimensionsError("Image dimensions must be positive integers")

        max_width = renderer.max_width
        max_height = renderer.max_height
        max_pixels = renderer.max_pixels
        if width > max_width or height > max_height or width * height > max_pixels:
            raise InvalidDimensionsError(
                f"Image exceeds renderer limits: {max_width}x{max_height}, "
                f"{max_pixels} total pixels"
            )
