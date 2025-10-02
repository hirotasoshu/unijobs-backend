from typing import Protocol

from src.application.view_models.vacancy import VacancyDetailViewModel, VacancyViewModel
from src.domain.value_object.employment_type import EmploymentType
from src.domain.value_object.ids import EmployerId, VacancyId
from src.domain.value_object.language import Language
from src.domain.value_object.workformat import WorkFormat


class VacancyViewReader(Protocol):
    async def get_views_by_filters(
        self,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
        salary_from: int | None = None,
        work_format: WorkFormat | None = None,
        employment_type: EmploymentType | None = None,
        employer_id: EmployerId | None = None,
        language: Language = Language.EN,
    ) -> list[VacancyViewModel]:
        raise NotImplementedError

    async def get_view_by_id(
        self, id: VacancyId, language: Language = Language.EN
    ) -> VacancyDetailViewModel | None:
        raise NotImplementedError


class VacancyReader(Protocol):
    async def count_by_filters(
        self,
        search: str | None = None,
        salary_from: int | None = None,
        work_format: WorkFormat | None = None,
        employment_type: EmploymentType | None = None,
        employer_id: EmployerId | None = None,
    ) -> int:
        raise NotImplementedError
