"""fix notifications body nullable

Revision ID: e4b7c2d1a9f0
Revises: f3c8b9a1d2e4
Create Date: 2026-02-04 21:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e4b7c2d1a9f0"
down_revision: Union[str, None] = "f3c8b9a1d2e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Only alter if the column exists (works on fresh DB + old DB)
    op.execute(
        """
        DO $$
        BEGIN
          IF EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'notifications'
              AND column_name = 'body'
          ) THEN
            ALTER TABLE notifications ALTER COLUMN body DROP NOT NULL;
          END IF;
        END $$;
        """
    )


def downgrade() -> None:
    # Downgrade only if column exists
    op.execute(
        """
        DO $$
        BEGIN
          IF EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'notifications'
              AND column_name = 'body'
          ) THEN
            ALTER TABLE notifications ALTER COLUMN body SET NOT NULL;
          END IF;
        END $$;
        """
    )
