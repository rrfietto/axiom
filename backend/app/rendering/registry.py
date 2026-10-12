from app.rendering.contracts import RendererDefinition
from app.rendering.exceptions import DuplicateRendererError, RendererNotFoundError
from app.rendering.renderers.wave_field import wave_field_renderer


class RendererRegistry:
    def __init__(self) -> None:
        self._renderers: dict[str, RendererDefinition] = {}

    def register(self, renderer: RendererDefinition) -> None:
        if renderer.id in self._renderers:
            raise DuplicateRendererError(
                f"Renderer '{renderer.id}' is already registered"
            )
        self._renderers[renderer.id] = renderer

    def get(self, renderer_id: str) -> RendererDefinition:
        try:
            return self._renderers[renderer_id]
        except KeyError as error:
            raise RendererNotFoundError(
                f"Renderer '{renderer_id}' is not registered"
            ) from error

    def all(self) -> tuple[RendererDefinition, ...]:
        return tuple(self._renderers[key] for key in sorted(self._renderers))


renderer_registry = RendererRegistry()
renderer_registry.register(wave_field_renderer)
