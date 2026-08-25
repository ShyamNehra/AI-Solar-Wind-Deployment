"""add infrastructure score note to site_scores

Revision ID: b18e2051ffd0
Revises: bd4f0124dce9
Create Date: 2026-08-11 19:20:54.137472

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b18e2051ffd0'
down_revision = 'bd4f0124dce9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('site_scores', sa.Column('infrastructure_score_note', sa.String(length=1000), nullable=True))


def downgrade() -> None:
    op.drop_column('site_scores', 'infrastructure_score_note')
