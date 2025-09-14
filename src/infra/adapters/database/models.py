from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.domain.value_object.employment_type import EmploymentType
from src.domain.value_object.ids import EmployerId, VacancyId
from src.domain.value_object.workformat import WorkFormat


class Base(DeclarativeBase):
    pass


class EmployerModel(Base):
    __tablename__: str = "employers"

    id: Mapped[EmployerId] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    avatar_url: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text(2000), nullable=True)

    vacancies: Mapped[list["VacancyModel"]] = relationship(
        back_populates="employer", cascade="all, delete-orphan"
    )


class VacancyModel(Base):
    __tablename__: str = "vacancies"

    id: Mapped[VacancyId] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(60), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(2000), nullable=True)
    location: Mapped[str] = mapped_column(String(60), nullable=False)

    salary_from: Mapped[int | None]
    salary_to: Mapped[int | None]

    work_format: Mapped[WorkFormat]
    employment_type: Mapped[EmploymentType]

    key_skills: Mapped[str | None]

    employer_id: Mapped[EmployerId] = mapped_column(ForeignKey("employers.id"))
    employer: Mapped["EmployerModel"] = relationship(back_populates="vacancies")
