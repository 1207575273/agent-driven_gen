"""add capacity analysis tables

Revision ID: f9897fc8b39e
Revises: 2d5acf20f8ae
Create Date: 2026-07-20 11:20:28.686096

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'f9897fc8b39e'
down_revision: str | None = '2d5acf20f8ae'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _ix_name(table: str, col: str) -> str:
    """索引名带表前缀, 避免跨表同名索引冲突 (如 work_hours.employee_id vs employees.employee_id)。"""
    return f"ix_{table}__{col}"


def upgrade() -> None:
    # --- 1. employees ---
    op.create_table("employees",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("employee_id", sa.String(50), nullable=True),
        sa.Column("position", sa.String(200), nullable=True),
        sa.Column("level1_dept", sa.String(200), nullable=True),
        sa.Column("level2_dept", sa.String(200), nullable=True),
        sa.Column("level3_dept", sa.String(200), nullable=True),
        sa.Column("level4_dept", sa.String(200), nullable=True),
        sa.Column("actual_team", sa.String(200), nullable=True),
        sa.Column("role", sa.String(200), nullable=True),
        sa.Column("employee_type", sa.String(100), nullable=True),
        sa.Column("employee_status", sa.String(50), nullable=True),
        sa.Column("position_type", sa.String(100), nullable=True),
        sa.Column("entry_date", sa.Date(), nullable=True),
        sa.Column("leave_date", sa.Date(), nullable=True),
        sa.Column("fill_note", sa.String(500), nullable=True),
        sa.Column("remarks", sa.String(1000), nullable=True),
        sa.Column("planned_project1", sa.String(500), nullable=True),
        sa.Column("planned_project2", sa.String(500), nullable=True),
        sa.Column("planned_project3", sa.String(500), nullable=True),
        sa.Column("planned_project4", sa.String(500), nullable=True),
        sa.Column("planned_project5", sa.String(500), nullable=True),
        sa.Column("is_excluded", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    for col in ["name", "employee_id", "level2_dept", "employee_status", "is_excluded"]:
        with op.batch_alter_table("employees") as b:
            b.create_index(_ix_name("employees", col), [col])

    # --- 2. project_categories ---
    op.create_table("project_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("category_name", sa.String(200), nullable=False),
        sa.Column("category_level", sa.Integer(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    with op.batch_alter_table("project_categories") as b:
        b.create_foreign_key("fk_project_categories__parent_id", "project_categories", ["parent_id"], ["id"])

    # --- 3. work_hours ---
    op.create_table("work_hours",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_name", sa.String(500), nullable=False),
        sa.Column("reporter", sa.String(200), nullable=False),
        sa.Column("reporter_department", sa.String(200), nullable=True),
        sa.Column("creator", sa.String(200), nullable=True),
        sa.Column("report_date", sa.Date(), nullable=False),
        sa.Column("hours", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("description", sa.String(2000), nullable=True),
        sa.Column("employee_id", sa.Integer(), nullable=True),
        sa.Column("matched_project_name", sa.String(500), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    for col in ["project_name", "report_date", "employee_id", "matched_project_name", "category_id"]:
        with op.batch_alter_table("work_hours") as b:
            b.create_index(_ix_name("work_hours", col), [col])
    with op.batch_alter_table("work_hours") as b:
        b.create_foreign_key("fk_work_hours__employee_id", "employees", ["employee_id"], ["id"])
        b.create_foreign_key("fk_work_hours__category_id", "project_categories", ["category_id"], ["id"])

    # --- 4. holidays ---
    op.create_table("holidays",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("holiday_name", sa.String(100), nullable=False),
        sa.Column("holiday_date", sa.Date(), nullable=False),
        sa.Column("is_workday", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    with op.batch_alter_table("holidays") as b:
        b.create_index(_ix_name("holidays", "holiday_date"), ["holiday_date"])

    # --- 5. should_be_capacity ---
    op.create_table("should_be_capacity",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("year_month", sa.String(7), nullable=False),
        sa.Column("total_working_days", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("active_working_days", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("capacity_days", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    for col in ["employee_id", "year_month"]:
        with op.batch_alter_table("should_be_capacity") as b:
            b.create_index(_ix_name("should_be_capacity", col), [col])
    with op.batch_alter_table("should_be_capacity") as b:
        b.create_foreign_key("fk_should_be_capacity__employee_id", "employees", ["employee_id"], ["id"])

    # --- 6. three_fast_plans ---
    op.create_table("three_fast_plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("plan_quarter", sa.String(10), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("plan_days", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    with op.batch_alter_table("three_fast_plans") as b:
        b.create_index(_ix_name("three_fast_plans", "category_id"), ["category_id"])
        b.create_foreign_key("fk_three_fast_plans__category_id", "project_categories", ["category_id"], ["id"])


def downgrade() -> None:
    # 按外键依赖顺序反向删除: 先删子表再删父表
    op.drop_table("three_fast_plans")
    op.drop_table("should_be_capacity")
    op.drop_table("holidays")
    op.drop_table("work_hours")
    op.drop_table("project_categories")
    op.drop_table("employees")
