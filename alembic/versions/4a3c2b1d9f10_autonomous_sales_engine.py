"""autonomous sales engine

Revision ID: 4a3c2b1d9f10
Revises: 8bfd52da4449
Create Date: 2026-03-25 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "4a3c2b1d9f10"
down_revision = "8bfd52da4449"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("leads", sa.Column("score_reason", sa.Text(), nullable=True))
    op.add_column("leads", sa.Column("priority_score", sa.Float(), nullable=True, server_default="0"))

    op.create_table(
        "lead_qualifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("current_question_index", sa.Integer(), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("plan_type", sa.String(length=30), nullable=True),
        sa.Column("urgency", sa.String(length=30), nullable=True),
        sa.Column("has_dependents", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lead_id"),
    )
    op.create_index("ix_qualification_tenant_status", "lead_qualifications", ["tenant_id", "status"], unique=False)

    op.create_table(
        "lead_cadences",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("step", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("context", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lead_id"),
    )
    op.create_index("ix_lead_cadence_tenant_status", "lead_cadences", ["tenant_id", "status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_lead_cadence_tenant_status", table_name="lead_cadences")
    op.drop_table("lead_cadences")

    op.drop_index("ix_qualification_tenant_status", table_name="lead_qualifications")
    op.drop_table("lead_qualifications")

    op.drop_column("leads", "priority_score")
    op.drop_column("leads", "score_reason")
