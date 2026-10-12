from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models import Preset
from app.db.session import get_db
from app.main import app


@pytest.fixture
def client() -> Generator[TestClient]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    test_session = sessionmaker(bind=engine, expire_on_commit=False)

    with test_session() as session:
        session.add_all(
            [
                Preset(
                    slug="test-waves",
                    name="Test Waves",
                    description="A visible preset",
                    renderer_id="wave-field",
                    parameter_overrides={
                        "line_count": {
                            "default": 20,
                            "maximum": 50,
                            "label": "Lines",
                        }
                    },
                    enabled=True,
                    sort_order=0,
                    source="system",
                    revision=2,
                ),
                Preset(
                    slug="hidden-waves",
                    name="Hidden Waves",
                    renderer_id="wave-field",
                    parameter_overrides={},
                    enabled=False,
                    sort_order=1,
                    source="system",
                    revision=1,
                ),
                Preset(
                    slug="broken-waves",
                    name="Broken Waves",
                    renderer_id="missing-renderer",
                    parameter_overrides={},
                    enabled=True,
                    sort_order=2,
                    source="system",
                    revision=1,
                ),
            ]
        )
        session.commit()

    def override_get_db() -> Generator[Session]:
        with test_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_list_presets_returns_only_available_enabled_presets(
    client: TestClient,
) -> None:
    response = client.get("/api/presets")

    assert response.status_code == 200
    presets = response.json()
    assert len(presets) == 1
    assert presets[0]["slug"] == "test-waves"
    assert presets[0]["renderer_id"] == "wave-field"
    assert presets[0]["renderer_version"] == 1
    assert presets[0]["revision"] == 2
    assert presets[0]["parameters"]["line_count"] == {
        "type": "integer",
        "default": 20,
        "minimum": 1,
        "maximum": 50,
        "options": [],
        "label": "Lines",
        "description": None,
    }


def test_get_preset_returns_merged_parameter_schema(client: TestClient) -> None:
    response = client.get("/api/presets/test-waves")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Test Waves"
    assert body["parameters"]["frequency"]["default"] == 2.0
    assert body["parameters"]["frequency"]["label"] == "Frequency"


@pytest.mark.parametrize("slug", ["missing", "hidden-waves", "broken-waves"])
def test_get_preset_returns_404_when_unavailable(client: TestClient, slug: str) -> None:
    response = client.get(f"/api/presets/{slug}")

    assert response.status_code == 404
