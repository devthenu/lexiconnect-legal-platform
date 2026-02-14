"""add actor columns to audit_logs

Revision ID: 9f3a2c1b7d9a
Revises: 5c2b1e05e123
Create Date: 2026-02-04 15:12:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "9f3a2c1b7d9a"
down_revision: Union[str, None] = "5c2b1e05e123"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns safely (fresh DB + reruns won't break)
    op.execute("ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS actor_user_id INTEGER")
    op.execute("ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS actor_email VARCHAR(255)")

    # Backfill only if legacy columns exist
    op.execute(
        """
        DO $$
        BEGIN
          -- Backfill actor_user_id from legacy user_id if present
          IF EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'audit_logs'
              AND column_name = 'user_id'
          ) THEN
            UPDATE audit_logs
            SET actor_user_id = user_id
            WHERE actor_user_id IS NULL;
          END IF;

          -- Backfill actor_email from legacy user_email if present
          IF EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'audit_logs'
              AND column_name = 'user_email'
          ) THEN
            UPDATE audit_logs
            SET actor_email = user_email
            WHERE actor_email IS NULL;
          END IF;
        END $$;
        """
    )

    # Create indexes safely (IF NOT EXISTS not supported by op.create_index, so use SQL)
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_actor_user_id ON audit_logs (actor_user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_actor_email ON audit_logs (actor_email)")


def downgrade() -> None:
    # Drop indexes safely
    op.execute("DROP INDEX IF EXISTS ix_audit_logs_actor_email")
    op.execute("DROP INDEX IF EXISTS ix_audit_logs_actor_user_id")

    # Drop columns (Postgres supports IF EXISTS for columns)
    op.execute("ALTER TABLE audit_logs DROP COLUMN IF EXISTS actor_email")
    op.execute("ALTER TABLE audit_logs DROP COLUMN IF EXISTS actor_user_id")
