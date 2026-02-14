"""add notifications body column

Revision ID: d333d54399f0
Revises: 158a6175562b
Create Date: 2026-02-14 03:34:25.298242

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd333d54399f0'
down_revision: Union[str, None] = '158a6175562b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    op.add_column("notifications", sa.Column("body", sa.Text(), nullable=True))

def downgrade():
    op.drop_column("notifications", "body")
















