import pytest
from PIL import Image

from app.rendering.contracts import RenderContext, RendererDefinition
from app.rendering.exceptions import DuplicateRendererError, RendererNotFoundError
from app.rendering.registry import RendererRegistry


def render_blank(context: RenderContext) -> Image.Image:
    return Image.new("RGB", (context.width, context.height))


def make_renderer(renderer_id: str) -> RendererDefinition:
    return RendererDefinition(
        id=renderer_id,
        version=1,
        name=renderer_id,
        parameters={},
        render=render_blank,
    )


def test_registry_registers_and_returns_renderer() -> None:
    registry = RendererRegistry()
    renderer = make_renderer("example")

    registry.register(renderer)

    assert registry.get("example") is renderer


def test_registry_rejects_duplicate_id() -> None:
    registry = RendererRegistry()
    registry.register(make_renderer("example"))

    with pytest.raises(DuplicateRendererError, match="already registered"):
        registry.register(make_renderer("example"))


def test_registry_reports_unknown_renderer() -> None:
    registry = RendererRegistry()

    with pytest.raises(RendererNotFoundError, match="missing"):
        registry.get("missing")


def test_registry_lists_renderers_in_stable_order() -> None:
    registry = RendererRegistry()
    registry.register(make_renderer("zebra"))
    registry.register(make_renderer("alpha"))

    assert [renderer.id for renderer in registry.all()] == ["alpha", "zebra"]
