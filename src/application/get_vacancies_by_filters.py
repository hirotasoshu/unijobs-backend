from dataclasses import dataclass
from math import ceil
from typing import Protocol, override

from src.application.common.interactor import Interactor
from src.application.common.vacancy_gateway import VacancyReader, VacancyViewReader
from src.application.view_models.vacancy import VacancyViewModel
from src.domain.value_object.employment_type import EmploymentType
from src.domain.value_object.ids import EmployerId
from src.domain.value_object.workformat import WorkFormat
from src.domain.exception.pagination import IncorrectPagination


@dataclass
class VacancyByFiltersDTO:
    page: int = 1
    page_size: int = 10
    search: str | None = None
    salary_from: int | None = None
    work_format: WorkFormat | None = None
    employment_type: EmploymentType | None = None
    employer_id: EmployerId | None = None


@dataclass
class VacancyByFiltersResultDTO:
    total: int
    total_pages: int
    result: list[VacancyViewModel]


class VacancyGateway(VacancyReader, VacancyViewReader, Protocol):
    pass


class GetVacanciesByFilters(Interactor[VacancyByFiltersDTO, VacancyByFiltersResultDTO]):
    def __init__(self, vacancy_gateway: VacancyGateway):
        self.vacancy_gateway: VacancyGateway = vacancy_gateway

    @override
    async def execute(self, data: VacancyByFiltersDTO) -> VacancyByFiltersResultDTO:
        if data.page < 1 or data.page_size > 500:
            raise IncorrectPagination(page=data.page, page_size=data.page_size)

        total = await self.vacancy_gateway.count_by_filters(
            search=data.search,
            salary_from=data.salary_from,
            work_format=data.work_format,
            employment_type=data.employment_type,
            employer_id=data.employer_id,
        )
        total_pages = ceil(total / data.page_size)
        result = await self.vacancy_gateway.get_views_by_filters(
            page=data.page,
            page_size=data.page_size,
            search=data.search,
            salary_from=data.salary_from,
            work_format=data.work_format,
            employment_type=data.employment_type,
            employer_id=data.employer_id,
        )
        return VacancyByFiltersResultDTO(
            result=result, total=total, total_pages=total_pages
        )
