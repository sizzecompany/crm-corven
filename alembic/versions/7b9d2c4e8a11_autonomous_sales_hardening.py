"""autonomous sales hardening

Revision ID: 7b9d2c4e8a11
Revises: 4a3c2b1d9f10
Create Date: 2026-03-25 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "7b9d2c4e8a11"
down_revision = "4a3c2b1d9f10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "outbox_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("aggregate_id", sa.String(length=80), nullable=True),
        sa.Column("event_name", sa.String(length=80), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("dedupe_key", sa.String(length=120), nullable=False),
        sa.Column("published", sa.Boolean(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("publish_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dedupe_key"),
    )
    op.create_index("ix_outbox_tenant_published", "outbox_events", ["tenant_id", "published", "created_at"], unique=False)

    op.create_table(
        "processed_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", sa.String(length=80), nullable=False),
        sa.Column("event_name", sa.String(length=80), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id"),
    )

    op.create_table(
        "conversation_states",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("state", sa.String(length=50), nullable=False),
        sa.Column("memory", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("last_message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["last_message_id"], ["messages.id"]),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lead_id"),
    )
    op.create_index("ix_conversation_state_tenant_lead", "conversation_states", ["tenant_id", "lead_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_conversation_state_tenant_lead", table_name="conversation_states")
    op.drop_table("conversation_states")

    op.drop_table("processed_events")

    op.drop_index("ix_outbox_tenant_published", table_name="outbox_events")
    op.drop_table("outbox_events")
