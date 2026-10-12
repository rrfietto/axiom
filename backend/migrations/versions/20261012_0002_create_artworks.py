"""Create artworks table.

Revision ID: 20261012_0002
Revises: 20261012_0001
"""

import sqlalchemy as sa
from alembic import op

revision = "20261012_0002"
down_revision = "20261012_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "artworks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("preset_id", sa.Integer(), nullable=False),
        sa.Column("preset_slug", sa.String(length=100), nullable=False),
        sa.Column("preset_name", sa.String(length=200), nullable=False),
        sa.Column("preset_revision", sa.Integer(), nullable=False),
        sa.Column("renderer_id", sa.String(length=100), nullable=False),
        sa.Column("renderer_version", sa.Integer(), nullable=False),
        sa.Column("parameters", sa.JSON(), nullable=False),
        sa.Column("seed", sa.Integer(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("image_path", sa.String(length=500), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["preset_id"], ["presets.id"]),
    )
    op.create_index("ix_artworks_preset_id", "artworks", ["preset_id"])
    op.create_index("ix_artworks_renderer_id", "artworks", ["renderer_id"])
    op.create_index("ix_artworks_created_at", "artworks", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_artworks_created_at", table_name="artworks")
    op.drop_index("ix_artworks_renderer_id", table_name="artworks")
    op.drop_index("ix_artworks_preset_id", table_name="artworks")
    op.drop_table("artworks")
