from dataclasses import dataclass

from src.application.view_models.employer import EmployerViewModel
from src.domain.value_object.employment_type import EmploymentType
from src.domain.value_object.ids import VacancyId
from src.domain.value_object.workformat import WorkFormat


@dataclass(kw_only=True)
class VacancyViewModel:
    id: VacancyId
    title: str
    salary_from: int
    salary_to: int
    employer: EmployerViewModel


@dataclass(kw_only=True)
class VacancyDetailViewModel(VacancyViewModel):
    key_skills: list[str]
    work_format: WorkFormat
    employment_type: EmploymentType
    description: str
    location: str
