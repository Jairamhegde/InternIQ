"""
Revision ID: 0002
Revises: 0001
Create Date: 2026-10-25
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

SCHEMAS = ("raw_data", "clean_data")


def upgrade() -> None:
    for schema in SCHEMAS:
        op.add_column(
            "job_data",
            sa.Column("source", sa.Text(), nullable=False, server_default="internshala"),
            schema=schema,
        )


def downgrade() -> None:
    for schema in SCHEMAS:
        op.drop_column("job_data", "source", schema=schema)
