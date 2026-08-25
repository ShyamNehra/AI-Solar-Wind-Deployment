"""initial migration

Revision ID: 000000000001
Revises: None
Create Date: 2026-07-26 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision = '000000000001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Enable PostGIS Extension
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # 2. Create Roles table
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_roles_id"), "roles", ["id"], unique=False)
    op.create_index(op.f("ix_roles_name"), "roles", ["name"], unique=True)

    # 3. Create Users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    # 4. Create User Roles association table
    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_id")
    )

    # 5. Create Projects table
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_projects_id"), "projects", ["id"], unique=False)

    # 6. Create Sites table (with Geometry POINT column)
    op.create_table(
        "sites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("geom", Geometry(geometry_type="POINT", srid=4326, from_text="ST_GeomFromEWKT", name="geometry"), nullable=False),
        sa.Column("land_area", sa.Float(), nullable=True),
        sa.Column("elevation", sa.Float(), nullable=True),
        sa.Column("existing_infrastructure", sa.String(length=1000), nullable=True),
        sa.Column("land_ownership", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_sites_id"), "sites", ["id"], unique=False)

    # 7. Create Site Environmental Data table
    op.create_table(
        "site_environmental_data",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("average_solar_irradiance", sa.Float(), nullable=True),
        sa.Column("average_wind_speed", sa.Float(), nullable=True),
        sa.Column("average_temperature", sa.Float(), nullable=True),
        sa.Column("average_elevation", sa.Float(), nullable=True),
        sa.Column("average_slope", sa.Float(), nullable=True),
        sa.Column("land_cover_type", sa.String(length=255), nullable=True),
        sa.Column("last_fetched_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("site_id")
    )
    op.create_index(op.f("ix_site_environmental_data_id"), "site_environmental_data", ["id"], unique=False)

    # 8. Create Deployment History table
    op.create_table(
        "deployment_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("changed_by_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["changed_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_deployment_history_id"), "deployment_history", ["id"], unique=False)

    # 9. Insert default roles
    op.execute("INSERT INTO roles (name) VALUES ('Planner')")
    op.execute("INSERT INTO roles (name) VALUES ('GIS Analyst')")
    op.execute("INSERT INTO roles (name) VALUES ('Project Manager')")
    op.execute("INSERT INTO roles (name) VALUES ('Administrator')")


def downgrade() -> None:
    op.drop_table("deployment_history")
    op.drop_table("site_environmental_data")
    op.drop_table("sites")
    op.drop_table("projects")
    op.drop_table("user_roles")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_roles_name"), table_name="roles")
    op.drop_index(op.f("ix_roles_id"), table_name="roles")
    op.drop_table("roles")
    op.execute("DROP EXTENSION IF EXISTS postgis")
