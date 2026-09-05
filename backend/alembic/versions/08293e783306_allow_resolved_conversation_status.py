from alembic import op


# revision identifiers, used by Alembic.
revision = "08293e783306"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "ck_conversations_status",
        "conversations",
        type_="check",
    )

    op.create_check_constraint(
        "ck_conversations_status",
        "conversations",
        "status IN ('open', 'pending', 'resolved')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_conversations_status",
        "conversations",
        type_="check",
    )

    op.create_check_constraint(
        "ck_conversations_status",
        "conversations",
        "status IN ('open', 'pending')",
    )