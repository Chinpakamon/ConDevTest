"""Initial migration

Revision ID: d91245147fc5
Revises: 
Create Date: 2026-06-19 17:06:19.205915

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd91245147fc5'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('bookings',
    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('appointment_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('service_type', sa.String(length=80), nullable=False),
    sa.Column('status', sa.Enum('pending', 'confirmed', 'failed', 'cancelled', name='booking_status'), nullable=False),
    sa.Column('notification_log', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_bookings'))
    )
    op.create_index(op.f('ix_bookings_appointment_at'), 'bookings', ['appointment_at'], unique=False)
    op.create_index(op.f('ix_bookings_id'), 'bookings', ['id'], unique=False)
    op.create_index(op.f('ix_bookings_status'), 'bookings', ['status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_bookings_status'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_appointment_at'), table_name='bookings')
    op.drop_table('bookings')
    sa.Enum(name="booking_status").drop(op.get_bind(), checkfirst=True)
