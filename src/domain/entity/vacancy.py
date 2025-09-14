from dataclasses import dataclass

from src.domain.value_object.employment_type import EmploymentType
from src.domain.value_object.ids import EmployerId, VacancyId
from src.domain.value_object.workformat import WorkFormat


@dataclass
class Vacancy:
    id: VacancyId
    title: str
    salary_from: int | None
    salary_to: int | None
    desription: str | None
    location: str
    key_skills: list[str]
    work_format: WorkFormat
    employment_type: EmploymentType
    employer_id: EmployerId
