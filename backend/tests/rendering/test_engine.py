from collections.abc import MutableMapping
from typing import cast

import pytest
from PIL import Image

from app.rendering.contracts import (
    ParameterDefinition,
    ParameterType,
    RenderContext,
    RendererDefinition,
    RendererFunction,
)
from app.rendering.engine import RenderingEngine
from app.rendering.exceptions import (
    InvalidDimensionsError,
    InvalidRendererOutputError,
    ParameterValidationError,
)
from app.rendering.registry import RendererRegistry


def make_engine(render_function: RendererFunction | None = None) -> RenderingEngine:
    def render(context: RenderContext) -> Image.Image:
        if render_function is not None:
            return render_function(context)
        return Image.new("RGB", (context.width, context.height))

    renderer = RendererDefinition(
        id="example",
        version=1,
        name="Example",
        parameters={
            "count": ParameterDefinition(
                ParameterType.INTEGER,
                default=10,
                minimum=1,
                maximum=20,
            ),
            "color": ParameterDefinition(ParameterType.COLOR, default="#102030"),
        },
        render=render,
        max_width=100,
        max_height=80,
        max_pixels=5_000,
    )
    registry = RendererRegistry()
    registry.register(renderer)
    return RenderingEngine(registry)


def test_engine_applies_defaults_and_passes_immutable_context() -> None:
    received: list[RenderContext] = []

    def capture(context: RenderContext) -> Image.Image:
        received.append(context)
        return Image.new("RGB", (context.width, context.height))

    engine = make_engine(capture)

    image = engine.render("example", width=40, height=30, seed=42)

    assert image.size == (40, 30)
    assert received[0].seed == 42
    assert received[0].parameters == {"count": 10, "color": "#102030"}
    mutable_parameters = cast(MutableMapping[str, object], received[0].parameters)
    with pytest.raises(TypeError):
        mutable_parameters["count"] = 12


def test_engine_applies_supplied_parameters() -> None:
    received: list[RenderContext] = []

    def capture(context: RenderContext) -> Image.Image:
        received.append(context)
        return Image.new("RGB", (context.width, context.height))

    engine = make_engine(capture)

    engine.render(
        "example",
        width=20,
        height=20,
        seed=0,
        parameters={"count": 15},
    )

    assert received[0].parameters["count"] == 15


def test_engine_rejects_unknown_parameter() -> None:
    engine = make_engine()

    with pytest.raises(ParameterValidationError, match="unknown"):
        engine.render(
            "example",
            width=20,
            height=20,
            seed=0,
            parameters={"unknown": 1},
        )


@pytest.mark.parametrize(
    ("width", "height"),
    [(0, 10), (101, 10), (100, 51)],
)
def test_engine_enforces_dimension_limits(width: int, height: int) -> None:
    engine = make_engine()

    with pytest.raises(InvalidDimensionsError):
        engine.render("example", width=width, height=height, seed=0)


def test_engine_rejects_invalid_seed() -> None:
    engine = make_engine()

    with pytest.raises(ParameterValidationError, match="seed"):
        engine.render("example", width=20, height=20, seed=-1)


def test_engine_rejects_wrong_output_size() -> None:
    def wrong_size(_: RenderContext) -> Image.Image:
        return Image.new("RGB", (1, 1))

    engine = make_engine(wrong_size)

    with pytest.raises(InvalidRendererOutputError, match="expected"):
        engine.render("example", width=20, height=20, seed=0)
