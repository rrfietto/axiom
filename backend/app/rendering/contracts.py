import math
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType

from PIL import Image

from app.rendering.exceptions import (
    ParameterValidationError,
    RendererConfigurationError,
)

type ParameterValue = int | float | bool | str
type RendererFunction = Callable[["RenderContext"], Image.Image]

_RENDERER_ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
_COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?$")


class ParameterType(StrEnum):
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    COLOR = "color"
    SELECT = "select"


@dataclass(frozen=True)
class ParameterDefinition:
    type: ParameterType
    default: ParameterValue
    minimum: int | float | None = None
    maximum: int | float | None = None
    options: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        is_numeric = self.type in (ParameterType.INTEGER, ParameterType.NUMBER)
        if not is_numeric and (self.minimum is not None or self.maximum is not None):
            raise RendererConfigurationError(
                "Only numeric parameters can declare minimum or maximum values"
            )
        if (
            self.minimum is not None
            and self.maximum is not None
            and self.minimum > self.maximum
        ):
            raise RendererConfigurationError("Parameter minimum cannot exceed maximum")
        if self.type is ParameterType.SELECT:
            if not self.options or len(set(self.options)) != len(self.options):
                raise RendererConfigurationError(
                    "Select parameters require unique, non-empty options"
                )
        elif self.options:
            raise RendererConfigurationError(
                "Only select parameters can declare options"
            )

        try:
            _ = self.validate("default", self.default)
        except ParameterValidationError as error:
            raise RendererConfigurationError(
                f"Invalid parameter default: {error}"
            ) from error

    def validate(self, name: str, value: object) -> ParameterValue:
        if self.type is ParameterType.INTEGER:
            if isinstance(value, bool) or not isinstance(value, int):
                raise ParameterValidationError(f"{name} must be an integer")
        elif self.type is ParameterType.NUMBER:
            if isinstance(value, bool) or not isinstance(value, int | float):
                raise ParameterValidationError(f"{name} must be a number")
            if not math.isfinite(value):
                raise ParameterValidationError(f"{name} must be finite")
        elif self.type is ParameterType.BOOLEAN:
            if not isinstance(value, bool):
                raise ParameterValidationError(f"{name} must be a boolean")
        elif self.type is ParameterType.COLOR:
            if not isinstance(value, str) or not _COLOR_PATTERN.fullmatch(value):
                raise ParameterValidationError(
                    f"{name} must be a hexadecimal RGB or RGBA color"
                )
        elif self.type is ParameterType.SELECT and (
            not isinstance(value, str) or value not in self.options
        ):
            raise ParameterValidationError(
                f"{name} must be one of: {', '.join(self.options)}"
            )

        if self.minimum is not None or self.maximum is not None:
            assert isinstance(value, int | float) and not isinstance(value, bool)
            if self.minimum is not None and value < self.minimum:
                raise ParameterValidationError(
                    f"{name} must be greater than or equal to {self.minimum}"
                )
            if self.maximum is not None and value > self.maximum:
                raise ParameterValidationError(
                    f"{name} must be less than or equal to {self.maximum}"
                )

        assert isinstance(value, int | float | bool | str)
        return value


@dataclass(frozen=True)
class RenderContext:
    width: int
    height: int
    seed: int
    parameters: Mapping[str, ParameterValue]


@dataclass(frozen=True)
class RendererDefinition:
    id: str
    version: int
    name: str
    parameters: Mapping[str, ParameterDefinition]
    render: RendererFunction
    max_width: int = 4096
    max_height: int = 4096
    max_pixels: int = 16_777_216

    def __post_init__(self) -> None:
        if not _RENDERER_ID_PATTERN.fullmatch(self.id):
            raise RendererConfigurationError(
                "Renderer id must be a lowercase, hyphen-separated identifier"
            )
        if self.version < 1:
            raise RendererConfigurationError("Renderer version must be positive")
        if not self.name.strip():
            raise RendererConfigurationError("Renderer name cannot be empty")
        if min(self.max_width, self.max_height, self.max_pixels) < 1:
            raise RendererConfigurationError(
                "Renderer dimension limits must be positive"
            )
        if any(not name.isidentifier() for name in self.parameters):
            raise RendererConfigurationError(
                "Renderer parameter names must be valid identifiers"
            )

        object.__setattr__(self, "parameters", MappingProxyType(dict(self.parameters)))
