"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-28
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "server_config",
        sa.Column("guild_id", sa.BigInteger, primary_key=True),
        sa.Column("starboard_channel_id", sa.BigInteger, nullable=False),
        sa.Column("threshold", sa.Integer, nullable=False, server_default="5"),
    )

    op.create_table(
        "pins",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("guild_id", sa.BigInteger, nullable=False, index=True),
        sa.Column("original_message_id", sa.BigInteger, nullable=False),
        sa.Column("original_channel_id", sa.BigInteger, nullable=False),
        sa.Column("starboard_message_id", sa.BigInteger, nullable=False),
        sa.UniqueConstraint("guild_id", "original_message_id", name="uq_pins_guild_message"),
    )

    op.create_table(
        "ignored_channels",
        sa.Column("guild_id", sa.BigInteger, nullable=False),
        sa.Column("channel_id", sa.BigInteger, nullable=False),
        sa.PrimaryKeyConstraint("guild_id", "channel_id"),
    )

    op.create_table(
        "ignored_reactions",
        sa.Column("guild_id", sa.BigInteger, nullable=False),
        sa.Column("emoji", sa.Text, nullable=False),
        sa.PrimaryKeyConstraint("guild_id", "emoji"),
    )


def downgrade():
    op.drop_table("ignored_reactions")
    op.drop_table("ignored_channels")
    op.drop_table("pins")
    op.drop_table("server_config")
