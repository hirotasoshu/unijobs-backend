from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import (
    Composite,
    DeclarativeBase,
    Mapped,
    composite,
    mapped_column,
    relationship,
)

from src.domain.value_object.application_status import ApplicationStatus
from src.domain.value_object.employment_type import EmploymentType
from src.domain.value_object.ids import ApplicationId, EmployerId, UserId, VacancyId
from src.domain.value_object.language import Language
from src.domain.value_object.workformat import WorkFormat


class Base(DeclarativeBase):
    pass


class LocalizedString:
    def __init__(self, en: str, ru: str, fr: str):
        self.en: str = en
        self.ru: str = ru
        self.fr: str = fr

    def __composite_values__(self):
        return self.en, self.ru, self.fr

    def __eq__(self, other):
        return (
            isinstance(other, LocalizedString)
            and self.en == other.en
            and self.ru == other.ru
            and self.fr == other.fr
        )

    def __repr__(self):
        return f"LocalizedString(en={self.en!r}, ru={self.ru!r}, fr={self.fr!r})"

    def get(self, language: Language) -> str:
        match language:
            case Language.RU:
                return self.ru
            case Language.FR:
                return self.fr
            case _:
                return self.en


class EmployerModel(Base):
    __tablename__: str = "employers"

    id: Mapped[EmployerId] = mapped_column(primary_key=True)
    avatar_url: Mapped[str | None] = mapped_column(String(100), nullable=True)

    name_en: Mapped[str] = mapped_column(String(30))
    name_ru: Mapped[str] = mapped_column(String(30))
    name_fr: Mapped[str] = mapped_column(String(30))

    description_en: Mapped[str | None] = mapped_column(Text(2000), nullable=True)
    description_ru: Mapped[str | None] = mapped_column(Text(2000), nullable=True)
    description_fr: Mapped[str | None] = mapped_column(Text(2000), nullable=True)

    name: Composite[LocalizedString] = composite(
        LocalizedString, name_en, name_ru, name_fr
    )

    description: Composite[LocalizedString] = composite(
        LocalizedString,
        description_en,
        description_ru,
        description_fr,
    )

    vacancies: Mapped[list["VacancyModel"]] = relationship(
        back_populates="employer", cascade="all, delete-orphan"
    )


class VacancyModel(Base):
    __tablename__: str = "vacancies"

    id: Mapped[VacancyId] = mapped_column(primary_key=True)

    title_en: Mapped[str] = mapped_column(String(60))
    title_ru: Mapped[str] = mapped_column(String(60))
    title_fr: Mapped[str] = mapped_column(String(60))

    description_en: Mapped[str | None] = mapped_column(Text(2000), nullable=True)
    description_ru: Mapped[str | None] = mapped_column(Text(2000), nullable=True)
    description_fr: Mapped[str | None] = mapped_column(Text(2000), nullable=True)

    location_en: Mapped[str] = mapped_column(String(60))
    location_ru: Mapped[str] = mapped_column(String(60))
    location_fr: Mapped[str] = mapped_column(String(60))

    salary_from: Mapped[int | None]
    salary_to: Mapped[int | None]

    work_format: Mapped[WorkFormat]
    employment_type: Mapped[EmploymentType]

    key_skills: Mapped[str | None]

    employer_id: Mapped[EmployerId] = mapped_column(ForeignKey("employers.id"))
    employer: Mapped["EmployerModel"] = relationship(back_populates="vacancies")
    applications: Mapped[list["ApplicationModel"]] = relationship(
        back_populates="vacancy", cascade="all, delete-orphan"
    )

    title: Composite[LocalizedString] = composite(
        LocalizedString, title_en, title_ru, title_fr
    )

    description: Composite[LocalizedString] = composite(
        LocalizedString,
        description_en,
        description_ru,
        description_fr,
    )

    location: Composite[LocalizedString] = composite(
        LocalizedString,
        location_en,
        location_ru,
        location_fr,
    )


class ApplicationModel(Base):
    __tablename__: str = "applications"

    id: Mapped[ApplicationId] = mapped_column(primary_key=True)
    status: Mapped[ApplicationStatus]
    cover_letter: Mapped[str] = mapped_column(Text(2000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    user_id: Mapped[UserId]

    vacancy_id: Mapped[VacancyId] = mapped_column(ForeignKey("vacancies.id"))
    vacancy: Mapped["VacancyModel"] = relationship(back_populates="applications")
