import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import Preset
from app.rendering.registry import renderer_registry
from app.services.preset_service import PresetConfigurationError, PresetService


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as database_session:
        yield database_session
    engine.dispose()


def make_preset(overrides: dict[str, object]) -> Preset:
    return Preset(
        id=1,
        slug="test",
        name="Test",
        renderer_id="wave-field",
        parameter_overrides=overrides,
        enabled=True,
        sort_order=0,
        source="user",
        revision=1,
    )


def test_preset_rejects_unknown_renderer_parameter(session: Session) -> None:
    service = PresetService(session, renderer_registry)
    session.add(make_preset({"missing": {"default": 1}}))
    session.commit()

    assert service.list_enabled() == []


def test_preset_rejects_limits_wider_than_renderer(session: Session) -> None:
    renderer = renderer_registry.get("wave-field")

    with pytest.raises(PresetConfigurationError, match="renderer limits"):
        PresetService._merge_parameters(
            renderer,
            {"line_count": {"maximum": 1000}},
        )


def test_preset_rejects_default_outside_effective_limits(session: Session) -> None:
    renderer = renderer_registry.get("wave-field")

    with pytest.raises(PresetConfigurationError, match="Invalid override"):
        PresetService._merge_parameters(
            renderer,
            {"line_count": {"default": 80, "maximum": 50}},
        )
