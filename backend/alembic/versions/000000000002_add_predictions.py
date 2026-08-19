"""add predictions and extend environmental columns

Revision ID: 000000000002
Revises: 000000000001
Create Date: 2026-07-26 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '000000000002'
down_revision = '000000000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create solar_predictions table
    op.create_table(
        "solar_predictions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("annual_irradiance", sa.Float(), nullable=False),
        sa.Column("peak_sun_hours", sa.Float(), nullable=False),
        sa.Column("expected_energy_output", sa.Float(), nullable=False),
        sa.Column("capacity_factor", sa.Float(), nullable=False),
        sa.Column("performance_ratio", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_solar_predictions_id"), "solar_predictions", ["id"], unique=False)

    # 2. Create wind_predictions table
    op.create_table(
        "wind_predictions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("average_wind_speed", sa.Float(), nullable=False),
        sa.Column("wind_power_density", sa.Float(), nullable=False),
        sa.Column("turbulence_intensity", sa.Float(), nullable=False),
        sa.Column("capacity_factor", sa.Float(), nullable=False),
        sa.Column("expected_annual_energy_production", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_wind_predictions_id"), "wind_predictions", ["id"], unique=False)

    # 3. Add average_wind_direction to site_environmental_data
    op.add_column("site_environmental_data", sa.Column("average_wind_direction", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("site_environmental_data", "average_wind_direction")
    op.drop_index(op.f("ix_wind_predictions_id"), table_name="wind_predictions")
    op.drop_table("wind_predictions")
    op.drop_index(op.f("ix_solar_predictions_id"), table_name="solar_predictions")
    op.drop_table("solar_predictions")
