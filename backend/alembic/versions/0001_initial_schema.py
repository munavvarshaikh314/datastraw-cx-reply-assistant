"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-08-29
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Required for gen_random_uuid()
    op.execute(
        'CREATE EXTENSION IF NOT EXISTS "pgcrypto"'
    )

    # ---------------------------------------------------------
    # Profiles
    # ---------------------------------------------------------

    op.create_table(
        "profiles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "auth.users.id",
                ondelete="CASCADE",
            ),
            primary_key=True,
        ),
        sa.Column(
            "full_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.String(length=50),
            nullable=False,
            server_default="agent",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "role IN ('agent', 'admin')",
            name="ck_profiles_role",
        ),
    )

    # ---------------------------------------------------------
    # Brands
    # ---------------------------------------------------------

    op.create_table(
        "brands",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text(
                "gen_random_uuid()"
            ),
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "slug",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "slug",
            name="uq_brands_slug",
        ),
    )

    op.create_index(
        "ix_brands_slug",
        "brands",
        ["slug"],
    )

    # ---------------------------------------------------------
    # Customers
    # ---------------------------------------------------------

    op.create_table(
        "customers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text(
                "gen_random_uuid()"
            ),
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(length=320),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # ---------------------------------------------------------
    # Conversations
    # ---------------------------------------------------------

    op.create_table(
        "conversations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text(
                "gen_random_uuid()"
            ),
        ),
        sa.Column(
            "brand_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "brands.id",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        sa.Column(
            "customer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "customers.id",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="open",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "status IN ('open', 'pending', 'resolved')",
            name="ck_conversations_status",
        ),
    )

    op.create_index(
        "ix_conversations_brand_id",
        "conversations",
        ["brand_id"],
    )

    op.create_index(
        "ix_conversations_customer_id",
        "conversations",
        ["customer_id"],
    )

    # ---------------------------------------------------------
    # Messages
    # ---------------------------------------------------------

    op.create_table(
        "messages",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text(
                "gen_random_uuid()"
            ),
        ),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "conversations.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "sender_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "sender_type IN ('customer', 'agent')",
            name="ck_messages_sender_type",
        ),
    )

    op.create_index(
        "ix_messages_conversation_created",
        "messages",
        ["conversation_id", "created_at"],
    )

    # ---------------------------------------------------------
    # Orders
    # ---------------------------------------------------------

    op.create_table(
        "orders",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text(
                "gen_random_uuid()"
            ),
        ),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "conversations.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "order_number",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "product_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "delivery_date",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "conversation_id",
            name="uq_orders_conversation_id",
        ),
        sa.UniqueConstraint(
            "order_number",
            name="uq_orders_order_number",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled')",
            name="ck_orders_status",
        ),
    )

    # ---------------------------------------------------------
    # Knowledge Documents
    # ---------------------------------------------------------

    op.create_table(
        "knowledge_documents",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text(
                "gen_random_uuid()"
            ),
        ),
        sa.Column(
            "brand_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "brands.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "document_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "version",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "document_type IN ('return', 'refund', 'shipping', 'cancellation')",
            name="ck_knowledge_documents_type",
        ),
        sa.CheckConstraint(
            "version > 0",
            name="ck_knowledge_documents_version",
        ),
        sa.UniqueConstraint(
            "brand_id",
            "document_type",
            "version",
            name="uq_knowledge_brand_type_version",
        ),
    )

    op.create_index(
        "ix_knowledge_documents_brand_id",
        "knowledge_documents",
        ["brand_id"],
    )

    # ---------------------------------------------------------
    # Reply Generations
    # ---------------------------------------------------------

    op.create_table(
        "reply_generations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text(
                "gen_random_uuid()"
            ),
        ),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "conversations.id",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "profiles.id",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        sa.Column(
            "generation_number",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
        sa.Column(
            "customer_message",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "retrieved_context",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "ai_response",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "edited_response",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "final_response",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="generated",
        ),
        sa.Column(
            "model",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "latency_ms",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "approved_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.CheckConstraint(
            "generation_number > 0",
            name="ck_reply_generation_number",
        ),
        sa.CheckConstraint(
            "status IN ('generated', 'edited', 'approved', 'rejected')",
            name="ck_reply_generation_status",
        ),
        sa.UniqueConstraint(
            "conversation_id",
            "generation_number",
            name="uq_reply_generation_conversation_number",
        ),
    )

    op.create_index(
        "ix_reply_generations_conversation_id",
        "reply_generations",
        ["conversation_id"],
    )

    op.create_index(
        "ix_reply_generations_agent_id",
        "reply_generations",
        ["agent_id"],
    )

    op.create_index(
        "ix_reply_generations_created_at",
        "reply_generations",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_reply_generations_created_at",
        table_name="reply_generations",
    )

    op.drop_index(
        "ix_reply_generations_agent_id",
        table_name="reply_generations",
    )

    op.drop_index(
        "ix_reply_generations_conversation_id",
        table_name="reply_generations",
    )

    op.drop_table("reply_generations")

    op.drop_index(
        "ix_knowledge_documents_brand_id",
        table_name="knowledge_documents",
    )

    op.drop_table("knowledge_documents")

    op.drop_table("orders")

    op.drop_index(
        "ix_messages_conversation_created",
        table_name="messages",
    )

    op.drop_table("messages")

    op.drop_index(
        "ix_conversations_customer_id",
        table_name="conversations",
    )

    op.drop_index(
        "ix_conversations_brand_id",
        table_name="conversations",
    )

    op.drop_table("conversations")

    op.drop_table("customers")

    op.drop_index(
        "ix_brands_slug",
        table_name="brands",
    )

    op.drop_table("brands")

    op.drop_table("profiles")