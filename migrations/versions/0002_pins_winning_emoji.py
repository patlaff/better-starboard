"""add winning_emoji to pins

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-29
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("pins", sa.Column("winning_emoji", sa.Text, nullable=False, server_default="⭐"))


def downgrade():
    op.drop_column("pins", "winning_emoji")
