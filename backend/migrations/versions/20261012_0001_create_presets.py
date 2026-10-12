"""Create presets table and initial wave field preset.

Revision ID: 20261012_0001
Revises: None
"""

from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

revision = "20261012_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    presets = op.create_table(
        "presets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("renderer_id", sa.String(length=100), nullable=False),
        sa.Column("parameter_overrides", sa.JSON(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_presets_slug", "presets", ["slug"], unique=True)
    op.create_index("ix_presets_renderer_id", "presets", ["renderer_id"])
    op.create_index("ix_presets_enabled", "presets", ["enabled"])

    now = datetime.now(UTC)
    op.bulk_insert(
        presets,
        [
            {
                "slug": "emerald-waves",
                "name": "Emerald Waves",
                "description": "Camadas de ondas orgânicas em tons de esmeralda.",
                "renderer_id": "wave-field",
                "parameter_overrides": {
                    "line_count": {"label": "Quantidade de linhas"},
                    "amplitude": {"label": "Amplitude"},
                    "frequency": {"label": "Frequência"},
                    "turbulence": {"label": "Turbulência"},
                    "stroke_width": {"label": "Espessura"},
                    "background": {"label": "Cor de fundo"},
                    "foreground": {"label": "Cor das linhas"},
                },
                "enabled": True,
                "sort_order": 0,
                "source": "system",
                "revision": 1,
                "created_at": now,
                "updated_at": now,
            }
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_presets_enabled", table_name="presets")
    op.drop_index("ix_presets_renderer_id", table_name="presets")
    op.drop_index("ix_presets_slug", table_name="presets")
    op.drop_table("presets")
