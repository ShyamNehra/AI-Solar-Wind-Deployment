"""add site scores and proximity columns

Revision ID: 000000000003
Revises: 000000000002
Create Date: 2026-07-26 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '000000000003'
down_revision = '000000000002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add columns to site_environmental_data
    op.add_column("site_environmental_data", sa.Column("nearest_road_km", sa.Float(), nullable=True))
    op.add_column("site_environmental_data", sa.Column("nearest_substation_km", sa.Float(), nullable=True))
    op.add_column("site_environmental_data", sa.Column("nearest_urban_area_km", sa.Float(), nullable=True))
    op.add_column("site_environmental_data", sa.Column("nearest_protected_zone_km", sa.Float(), nullable=True))
    op.add_column("site_environmental_data", sa.Column("nearest_water_body_km", sa.Float(), nullable=True))

    # 2. Create site_scores table
    op.create_table(
        "site_scores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("solar_score", sa.Float(), nullable=True),
        sa.Column("wind_score", sa.Float(), nullable=True),
        sa.Column("renewable_resource_score", sa.Float(), nullable=True),
        sa.Column("geographic_score", sa.Float(), nullable=True),
        sa.Column("infrastructure_score", sa.Float(), nullable=True),
        sa.Column("environmental_score", sa.Float(), nullable=True),
        sa.Column("economic_score", sa.Float(), nullable=True),
        sa.Column("overall_deployment_score", sa.Float(), nullable=True),
        sa.Column("suitability_category", sa.String(length=50), nullable=True),
        sa.Column("formula_used", sa.String(length=1000), nullable=True),
        sa.Column("formula_source", sa.String(length=1000), nullable=True),
        sa.Column("economic_score_note", sa.String(length=1000), nullable=True),
        sa.Column("environmental_score_note", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("site_id")
    )
    op.create_index(op.f("ix_site_scores_id"), "site_scores", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_site_scores_id"), table_name="site_scores")
    op.drop_table("site_scores")
    op.drop_column("site_environmental_data", "nearest_water_body_km")
    op.drop_column("site_environmental_data", "nearest_protected_zone_km")
    op.drop_column("site_environmental_data", "nearest_urban_area_km")
    op.drop_column("site_environmental_data", "nearest_substation_km")
    op.drop_column("site_environmental_data", "nearest_road_km")
