import math
from typing import cast

import numpy as np
from PIL import Image, ImageColor, ImageDraw

from app.rendering.contracts import (
    ParameterDefinition,
    ParameterType,
    RenderContext,
    RendererDefinition,
)


def render_wave_field(context: RenderContext) -> Image.Image:
    line_count = cast(int, context.parameters["line_count"])
    amplitude = float(context.parameters["amplitude"])
    frequency = float(context.parameters["frequency"])
    turbulence = float(context.parameters["turbulence"])
    stroke_width = cast(int, context.parameters["stroke_width"])
    background = cast(str, context.parameters["background"])
    foreground = cast(str, context.parameters["foreground"])

    image = Image.new(
        "RGB",
        (context.width, context.height),
        ImageColor.getcolor(background, "RGB"),
    )
    draw = ImageDraw.Draw(image)
    color = ImageColor.getcolor(foreground, "RGB")
    random = np.random.default_rng(context.seed)

    x_coordinates = np.linspace(0, context.width - 1, max(context.width, 2))
    normalized_x = x_coordinates / max(context.width - 1, 1)
    baselines = np.linspace(
        -amplitude,
        context.height + amplitude,
        line_count,
    )

    for baseline in baselines:
        phase = random.uniform(0, math.tau)
        secondary_phase = random.uniform(0, math.tau)
        local_amplitude = amplitude * random.uniform(0.7, 1.15)
        primary_wave = np.sin(math.tau * frequency * normalized_x + phase)
        secondary_wave = np.sin(
            math.tau * frequency * 2.7 * normalized_x + secondary_phase
        )
        y_coordinates = baseline + local_amplitude * (
            primary_wave + turbulence * secondary_wave
        )
        x_values = x_coordinates.tolist()
        y_values = y_coordinates.tolist()
        points = list(zip(x_values, y_values, strict=True))
        draw.line(points, fill=color, width=stroke_width, joint="curve")

    return image


wave_field_renderer = RendererDefinition(
    id="wave-field",
    version=1,
    name="Wave Field",
    parameters={
        "line_count": ParameterDefinition(
            type=ParameterType.INTEGER,
            default=36,
            minimum=1,
            maximum=200,
        ),
        "amplitude": ParameterDefinition(
            type=ParameterType.NUMBER,
            default=28.0,
            minimum=0.0,
            maximum=500.0,
        ),
        "frequency": ParameterDefinition(
            type=ParameterType.NUMBER,
            default=2.0,
            minimum=0.1,
            maximum=20.0,
        ),
        "turbulence": ParameterDefinition(
            type=ParameterType.NUMBER,
            default=0.2,
            minimum=0.0,
            maximum=1.0,
        ),
        "stroke_width": ParameterDefinition(
            type=ParameterType.INTEGER,
            default=2,
            minimum=1,
            maximum=12,
        ),
        "background": ParameterDefinition(
            type=ParameterType.COLOR,
            default="#07100f",
        ),
        "foreground": ParameterDefinition(
            type=ParameterType.COLOR,
            default="#74e6c2",
        ),
    },
    render=render_wave_field,
    max_width=4096,
    max_height=4096,
    max_pixels=16_777_216,
)
