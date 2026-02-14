"""add notifications meta column

Revision ID: 9adce03e0045
Revises: d333d54399f0
Create Date: 2026-02-14 03:44:43.682701

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9adce03e0045'
down_revision: Union[str, None] = 'd333d54399f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    op.add_column("notifications", sa.Column("meta", sa.JSON(), nullable=True))

def downgrade():
    op.drop_column("notifications", "meta")















