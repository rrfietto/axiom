from io import BytesIO

from PIL import Image

from app.rendering.engine import RenderingEngine
from app.rendering.registry import renderer_registry


def render_wave_field(seed: int) -> Image.Image:
    engine = RenderingEngine(renderer_registry)
    return engine.render(
        "wave-field",
        width=160,
        height=120,
        seed=seed,
    )


def test_wave_field_is_registered() -> None:
    renderer = renderer_registry.get("wave-field")

    assert renderer.version == 1
    assert renderer.name == "Wave Field"


def test_wave_field_uses_declared_defaults() -> None:
    image = render_wave_field(seed=42)

    assert image.mode == "RGB"
    assert image.size == (160, 120)
    assert image.getbbox() is not None
    assert len(image.getcolors(maxcolors=160 * 120) or []) > 1


def test_wave_field_is_deterministic_for_same_seed() -> None:
    first = render_wave_field(seed=123)
    second = render_wave_field(seed=123)

    assert first.tobytes() == second.tobytes()


def test_wave_field_changes_with_seed() -> None:
    first = render_wave_field(seed=123)
    second = render_wave_field(seed=456)

    assert first.tobytes() != second.tobytes()


def test_wave_field_can_be_serialized_as_png() -> None:
    output = BytesIO()
    render_wave_field(seed=42).save(output, format="PNG")
    output.seek(0)

    decoded = Image.open(output)

    assert decoded.format == "PNG"
    assert decoded.size == (160, 120)
