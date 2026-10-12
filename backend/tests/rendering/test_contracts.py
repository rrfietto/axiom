from collections.abc import MutableMapping
from typing import cast

import pytest
from PIL import Image

from app.rendering.contracts import (
    ParameterDefinition,
    ParameterType,
    RenderContext,
    RendererDefinition,
)
from app.rendering.exceptions import (
    ParameterValidationError,
    RendererConfigurationError,
)


def render_blank(context: RenderContext) -> Image.Image:
    return Image.new("RGB", (context.width, context.height))


def test_renderer_contract_is_immutable() -> None:
    source_parameters = {
        "iterations": ParameterDefinition(
            type=ParameterType.INTEGER,
            default=10,
            minimum=1,
            maximum=100,
        )
    }
    renderer = RendererDefinition(
        id="test-renderer",
        version=1,
        name="Test renderer",
        parameters=source_parameters,
        render=render_blank,
    )

    source_parameters.clear()

    assert tuple(renderer.parameters) == ("iterations",)
    mutable_parameters = cast(
        MutableMapping[str, ParameterDefinition], renderer.parameters
    )
    with pytest.raises(TypeError):
        mutable_parameters["other"] = ParameterDefinition(
            type=ParameterType.BOOLEAN,
            default=True,
        )


def test_parameter_definition_rejects_invalid_default() -> None:
    with pytest.raises(RendererConfigurationError, match="Invalid parameter default"):
        ParameterDefinition(
            type=ParameterType.INTEGER,
            default=0,
            minimum=1,
        )


@pytest.mark.parametrize(
    ("definition", "value"),
    [
        (ParameterDefinition(ParameterType.INTEGER, 1), True),
        (ParameterDefinition(ParameterType.NUMBER, 1.0), float("nan")),
        (ParameterDefinition(ParameterType.BOOLEAN, False), "false"),
        (ParameterDefinition(ParameterType.COLOR, "#112233"), "blue"),
        (
            ParameterDefinition(
                ParameterType.SELECT,
                "square",
                options=("square", "circle"),
            ),
            "triangle",
        ),
    ],
)
def test_parameter_definition_rejects_invalid_values(
    definition: ParameterDefinition, value: object
) -> None:
    with pytest.raises(ParameterValidationError):
        definition.validate("shape", value)


def test_renderer_rejects_invalid_id() -> None:
    with pytest.raises(RendererConfigurationError, match="Renderer id"):
        RendererDefinition(
            id="Invalid ID",
            version=1,
            name="Invalid",
            parameters={},
            render=render_blank,
        )
