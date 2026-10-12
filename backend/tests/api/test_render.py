from collections.abc import Generator
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image
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
        session.add(
            Preset(
                slug="test-waves",
                name="Test Waves",
                renderer_id="wave-field",
                parameter_overrides={"line_count": {"default": 20, "maximum": 50}},
                enabled=True,
                sort_order=0,
                source="system",
                revision=1,
            )
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


def render(client: TestClient, **overrides: object):
    payload: dict[str, object] = {
        "preset_slug": "test-waves",
        "width": 160,
        "height": 120,
        "seed": 42,
        "parameters": {},
    }
    payload.update(overrides)
    return client.post("/api/render", json=payload)


def test_render_returns_png(client: TestClient) -> None:
    response = render(client)

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.headers["x-axiom-preset"] == "test-waves"
    assert response.headers["x-axiom-seed"] == "42"

    image = Image.open(BytesIO(response.content))
    assert image.format == "PNG"
    assert image.mode == "RGB"
    assert image.size == (160, 120)


def test_render_is_deterministic(client: TestClient) -> None:
    first = render(client)
    second = render(client)

    assert first.content == second.content


def test_render_accepts_parameter_overrides(client: TestClient) -> None:
    default = render(client)
    customized = render(
        client,
        parameters={"line_count": 8, "foreground": "#ff0000"},
    )

    assert customized.status_code == 200
    assert customized.content != default.content


@pytest.mark.parametrize(
    "overrides",
    [
        {"parameters": {"line_count": 51}},
        {"parameters": {"unknown": 1}},
        {"width": 5000},
        {"seed": -1},
    ],
)
def test_render_rejects_invalid_input(
    client: TestClient,
    overrides: dict[str, object],
) -> None:
    response = render(client, **overrides)

    assert response.status_code == 422


def test_render_returns_404_for_missing_preset(client: TestClient) -> None:
    response = render(client, preset_slug="missing")

    assert response.status_code == 404
