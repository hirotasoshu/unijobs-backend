"""create initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-01 00:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "employers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("avatar_url", sa.String(length=100), nullable=True),
        sa.Column("name_en", sa.String(length=30), nullable=False),
        sa.Column("name_ru", sa.String(length=30), nullable=False),
        sa.Column("name_fr", sa.String(length=30), nullable=False),
        sa.Column("description_en", sa.Text(length=2000), nullable=True),
        sa.Column("description_ru", sa.Text(length=2000), nullable=True),
        sa.Column("description_fr", sa.Text(length=2000), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=256), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "vacancies",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title_en", sa.String(length=60), nullable=False),
        sa.Column("title_ru", sa.String(length=60), nullable=False),
        sa.Column("title_fr", sa.String(length=60), nullable=False),
        sa.Column("description_en", sa.Text(length=2000), nullable=True),
        sa.Column("description_ru", sa.Text(length=2000), nullable=True),
        sa.Column("description_fr", sa.Text(length=2000), nullable=True),
        sa.Column("location_en", sa.String(length=60), nullable=False),
        sa.Column("location_ru", sa.String(length=60), nullable=False),
        sa.Column("location_fr", sa.String(length=60), nullable=False),
        sa.Column("salary_from", sa.Integer(), nullable=True),
        sa.Column("salary_to", sa.Integer(), nullable=True),
        sa.Column(
            "work_format",
            sa.Enum("REMOTE", "ONSITE", "HYBRID", name="workformat"),
            nullable=False,
        ),
        sa.Column(
            "employment_type",
            sa.Enum(
                "FULL_TIME",
                "PART_TIME",
                "INTERNSHIP",
                "TEMPORARY",
                name="employmenttype",
            ),
            nullable=False,
        ),
        sa.Column("key_skills", sa.String(), nullable=True),
        sa.Column("employer_id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "applications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PENDING", "REVIEW", "ACCEPTED", "REJECTED", name="applicationstatus"),
            nullable=False,
        ),
        sa.Column("cover_letter", sa.Text(length=2000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("vacancy_id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("applications")
    op.drop_table("vacancies")
    op.drop_table("users")
    op.drop_table("employers")
