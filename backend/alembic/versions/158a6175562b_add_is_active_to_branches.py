"""add is_active to branches

Revision ID: 158a6175562b
Revises: e4b7c2d1a9f0
Create Date: 2026-02-14 08:47:30.896661

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '158a6175562b'
down_revision: Union[str, None] = 'e4b7c2d1a9f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "branches",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    # optional: drop default after backfill
    op.alter_column("branches", "is_active", server_default=None)

def downgrade():
    op.drop_column("branches", "is_active")
















