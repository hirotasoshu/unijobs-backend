from pydantic import BaseModel

from src.domain.value_object.employment_type import EmploymentType
from src.domain.value_object.ids import EmployerId
from src.domain.value_object.workformat import WorkFormat


class VacancyFilters(BaseModel):
    page: int = 1
    page_size: int = 10
    search: str | None = None
    salary_from: int | None = None
    work_format: WorkFormat | None = None
    employment_type: EmploymentType | None = None
    employer_id: EmployerId | None = None
