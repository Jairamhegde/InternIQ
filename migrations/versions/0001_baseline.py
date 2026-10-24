"""Baseline: the schema as it existed before Alembic was added

The raw_data and clean_data tables were created by hand, so this revision does
nothing. On the existing database, mark it as applied once with:

    alembic stamp 0001

Every later schema change is a new revision on top of this one.

Revision ID: 0001
Revises:
Create Date: 2026-10-25
"""

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
