from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Preset
from app.rendering.contracts import ParameterDefinition, RendererDefinition
from app.rendering.exceptions import (
    ParameterValidationError,
    RendererConfigurationError,
    RendererNotFoundError,
)
from app.rendering.registry import RendererRegistry
from app.schemas.preset import ParameterSchema, PresetResponse

_ALLOWED_OVERRIDE_FIELDS = {
    "default",
    "minimum",
    "maximum",
    "label",
    "description",
}


class PresetNotFoundError(Exception):
    pass


class PresetConfigurationError(Exception):
    pass


@dataclass(frozen=True)
class ResolvedPreset:
    preset: Preset
    renderer: RendererDefinition
    parameters: dict[str, ParameterSchema]


class PresetService:
    def __init__(self, session: Session, registry: RendererRegistry) -> None:
        self._session = session
        self._registry = registry

    def list_enabled(self) -> list[PresetResponse]:
        statement = (
            select(Preset)
            .where(Preset.enabled.is_(True))
            .order_by(Preset.sort_order, Preset.name)
        )
        presets = self._session.scalars(statement).all()
        responses: list[PresetResponse] = []
        for preset in presets:
            try:
                responses.append(self._to_response(self._resolve(preset)))
            except (PresetConfigurationError, RendererNotFoundError):
                continue
        return responses

    def get_enabled(self, slug: str) -> PresetResponse:
        return self._to_response(self.resolve_enabled(slug))

    def resolve_enabled(self, slug: str) -> ResolvedPreset:
        statement = select(Preset).where(
            Preset.slug == slug,
            Preset.enabled.is_(True),
        )
        preset = self._session.scalar(statement)
        if preset is None:
            raise PresetNotFoundError(f"Preset '{slug}' was not found")
        try:
            return self._resolve(preset)
        except (PresetConfigurationError, RendererNotFoundError) as error:
            raise PresetNotFoundError(f"Preset '{slug}' is unavailable") from error

    def _resolve(self, preset: Preset) -> ResolvedPreset:
        renderer = self._registry.get(preset.renderer_id)
        return ResolvedPreset(
            preset=preset,
            renderer=renderer,
            parameters=self._merge_parameters(renderer, preset.parameter_overrides),
        )

    @staticmethod
    def _to_response(resolved: ResolvedPreset) -> PresetResponse:
        return PresetResponse(
            id=resolved.preset.id,
            slug=resolved.preset.slug,
            name=resolved.preset.name,
            description=resolved.preset.description,
            renderer_id=resolved.renderer.id,
            renderer_version=resolved.renderer.version,
            parameters=resolved.parameters,
            revision=resolved.preset.revision,
        )

    @staticmethod
    def _merge_parameters(
        renderer: RendererDefinition,
        overrides: dict[str, Any],
    ) -> dict[str, ParameterSchema]:
        unknown_parameters = overrides.keys() - renderer.parameters.keys()
        if unknown_parameters:
            names = ", ".join(sorted(unknown_parameters))
            raise PresetConfigurationError(f"Unknown preset parameters: {names}")

        result: dict[str, ParameterSchema] = {}
        for name, definition in renderer.parameters.items():
            raw_override = overrides.get(name, {})
            if not isinstance(raw_override, dict):
                raise PresetConfigurationError(
                    f"Override for '{name}' must be an object"
                )
            unknown_fields = raw_override.keys() - _ALLOWED_OVERRIDE_FIELDS
            if unknown_fields:
                fields = ", ".join(sorted(unknown_fields))
                raise PresetConfigurationError(
                    f"Unknown override fields for '{name}': {fields}"
                )
            result[name] = PresetService._merge_parameter(
                name,
                definition,
                raw_override,
            )
        return result

    @staticmethod
    def _merge_parameter(
        name: str,
        definition: ParameterDefinition,
        override: dict[str, Any],
    ) -> ParameterSchema:
        minimum = override.get("minimum", definition.minimum)
        maximum = override.get("maximum", definition.maximum)
        if definition.minimum is not None and (
            minimum is None or minimum < definition.minimum
        ):
            raise PresetConfigurationError(
                f"Preset minimum for '{name}' exceeds renderer limits"
            )
        if definition.maximum is not None and (
            maximum is None or maximum > definition.maximum
        ):
            raise PresetConfigurationError(
                f"Preset maximum for '{name}' exceeds renderer limits"
            )

        try:
            merged = ParameterDefinition(
                type=definition.type,
                default=override.get("default", definition.default),
                minimum=minimum,
                maximum=maximum,
                options=definition.options,
            )
        except (ParameterValidationError, RendererConfigurationError) as error:
            raise PresetConfigurationError(
                f"Invalid override for '{name}': {error}"
            ) from error

        return ParameterSchema(
            type=merged.type,
            default=merged.default,
            minimum=merged.minimum,
            maximum=merged.maximum,
            options=merged.options,
            label=str(override.get("label", name.replace("_", " ").title())),
            description=override.get("description"),
        )
