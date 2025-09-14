from dataclasses import dataclass
from typing import Protocol, override

from src.application.common.interactor import Interactor
from src.application.common.vacancy_gateway import VacancyViewReader
from src.application.view_models.vacancy import VacancyDetailViewModel
from src.domain.exception.vacancy import VacancyNotFoundError
from src.domain.value_object.ids import VacancyId


@dataclass
class VacancyByIdDTO:
    vacancy_id: VacancyId


class VacancyGateway(VacancyViewReader, Protocol):
    pass


class GetVacancyById(Interactor[VacancyByIdDTO, VacancyDetailViewModel]):
    def __init__(self, vacancy_gateway: VacancyGateway):
        self.vacancy_gateway: VacancyGateway = vacancy_gateway

    @override
    async def execute(self, data: VacancyByIdDTO) -> VacancyDetailViewModel:
        result = await self.vacancy_gateway.get_view_by_id(data.vacancy_id)
        if not result:
            raise VacancyNotFoundError(data.vacancy_id)
        return result
