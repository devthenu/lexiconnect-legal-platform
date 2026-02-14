"""Enhanced token queue schema with additional fields

Revision ID: 001_enhance_token_queue
Revises: None
Create Date: 2026-01-23 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_enhance_token_queue'
down_revision = None
branch_labels = None
depends_on = None

EXPECTED_STATUS_VALUES = (
    'pending',
    'confirmed',
    'in_progress',
    'completed',
    'cancelled',
    'no_show',
)


def _enum_exists(bind, enum_name: str) -> bool:
    row = bind.execute(
        sa.text(
            """
            SELECT 1
            FROM pg_type t
            WHERE t.typname = :enum_name
            LIMIT 1
            """
        ),
        {"enum_name": enum_name},
    ).first()
    return row is not None


def _get_enum_labels(bind, enum_name: str) -> set[str]:
    rows = bind.execute(
        sa.text(
            """
            SELECT e.enumlabel
            FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = :enum_name
            ORDER BY e.enumsortorder
            """
        ),
        {"enum_name": enum_name},
    )
    return {row[0] for row in rows}


def _ensure_token_queue_status_enum(bind) -> None:
    if bind.dialect.name != "postgresql":
        return

    if not _enum_exists(bind, "token_queue_status"):
        enum_values_sql = ", ".join(f"'{value}'" for value in EXPECTED_STATUS_VALUES)
        op.execute(f"CREATE TYPE token_queue_status AS ENUM ({enum_values_sql})")
        return

    existing_labels = _get_enum_labels(bind, "token_queue_status")
    missing_values = [value for value in EXPECTED_STATUS_VALUES if value not in existing_labels]
    if not missing_values:
        return

    # PostgreSQL requires enum value additions to be committed before those values are used.
    with op.get_context().autocommit_block():
        for value in missing_values:
            op.execute(f"ALTER TYPE token_queue_status ADD VALUE IF NOT EXISTS '{value}'")


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    table_names = set(inspector.get_table_names())
    _ensure_token_queue_status_enum(bind)

    if 'token_queue' not in table_names:
        status_enum_for_column = postgresql.ENUM(
            *EXPECTED_STATUS_VALUES,
            name='token_queue_status',
            create_type=False,
        )
        op.create_table(
            'token_queue',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('date', sa.Date(), nullable=False),
            sa.Column('token_number', sa.Integer(), nullable=False),
            sa.Column('lawyer_id', sa.Integer(), nullable=False),
            sa.Column('client_id', sa.Integer(), nullable=False),
            sa.Column('status', status_enum_for_column, nullable=False, server_default=sa.text("'pending'")),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('lawyer_id', 'date', 'token_number', name='uq_token_queue_lawyer_date_token_number'),
        )

    inspector = inspect(bind)
    table_names = set(inspector.get_table_names())
    if 'token_queue' not in table_names:
        return

    existing_columns = {col['name'] for col in inspector.get_columns('token_queue')}

    columns_to_add = [
        ('time', sa.Column('time', sa.String(8), nullable=True)),
        ('branch_id', sa.Column('branch_id', sa.Integer(), nullable=True)),
        ('reason', sa.Column('reason', sa.String(255), nullable=True)),
        ('notes', sa.Column('notes', sa.Text(), nullable=True)),
        ('started_at', sa.Column('started_at', sa.DateTime(timezone=True), nullable=True)),
        ('completed_at', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True)),
        ('created_at', sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()"))),
        ('updated_at', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()"))),
    ]

    for name, column in columns_to_add:
        if name not in existing_columns:
            op.add_column('token_queue', column)

    inspector = inspect(bind)
    existing_columns = {col['name'] for col in inspector.get_columns('token_queue')}
    existing_indexes = {idx['name'] for idx in inspector.get_indexes('token_queue')}

    if 'time' in existing_columns and 'ix_token_queue_time' not in existing_indexes:
        op.create_index('ix_token_queue_time', 'token_queue', ['time'], unique=False)
    if 'branch_id' in existing_columns and 'ix_token_queue_branch_id' not in existing_indexes:
        op.create_index('ix_token_queue_branch_id', 'token_queue', ['branch_id'], unique=False)
    if 'status' in existing_columns and 'ix_token_queue_status' not in existing_indexes:
        op.create_index('ix_token_queue_status', 'token_queue', ['status'], unique=False)

    if 'branch_id' in existing_columns and 'branches' in table_names:
        existing_fks = inspector.get_foreign_keys('token_queue')
        has_branch_fk = any(
            fk.get('name') == 'fk_token_queue_branch_id' or fk.get('constrained_columns') == ['branch_id']
            for fk in existing_fks
        )
        if not has_branch_fk:
            op.create_foreign_key(
                'fk_token_queue_branch_id',
                'token_queue',
                'branches',
                ['branch_id'],
                ['id'],
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if 'token_queue' not in set(inspector.get_table_names()):
        return

    existing_columns = {col['name'] for col in inspector.get_columns('token_queue')}
    existing_indexes = {idx['name'] for idx in inspector.get_indexes('token_queue')}
    existing_fks = inspector.get_foreign_keys('token_queue')

    if 'ix_token_queue_status' in existing_indexes:
        op.drop_index('ix_token_queue_status', table_name='token_queue')
    if 'ix_token_queue_branch_id' in existing_indexes:
        op.drop_index('ix_token_queue_branch_id', table_name='token_queue')
    if 'ix_token_queue_time' in existing_indexes:
        op.drop_index('ix_token_queue_time', table_name='token_queue')

    if any(
        fk.get('name') == 'fk_token_queue_branch_id' or fk.get('constrained_columns') == ['branch_id']
        for fk in existing_fks
    ):
        op.drop_constraint('fk_token_queue_branch_id', 'token_queue', type_='foreignkey')

    for column_name in ['updated_at', 'created_at', 'completed_at', 'started_at', 'notes', 'reason', 'branch_id', 'time']:
        if column_name in existing_columns:
            op.drop_column('token_queue', column_name)

    # Intentionally leave enum changes as-is for safe, non-destructive downgrade behavior.
