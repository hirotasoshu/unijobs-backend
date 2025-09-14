from dataclasses import dataclass
from typing import Protocol, override

from src.application.common.application_gateway import ApplicationViewReader
from src.application.common.interactor import Interactor
from src.application.view_models.application import ApplicationDetailViewModel
from src.domain.exception.application import UserApplicationForVacancyNotFound
from src.domain.value_object.ids import UserId, VacancyId


@dataclass
class GetUserApplicationForVacancyDTO:
    vacancy_id: VacancyId
    user_id: UserId


class ApplicationGateway(ApplicationViewReader, Protocol):
    pass


class GetUserApplicationForVacancy(
    Interactor[GetUserApplicationForVacancyDTO, ApplicationDetailViewModel]
):
    def __init__(self, application_gateway: ApplicationGateway):
        self.application_gateway: ApplicationGateway = application_gateway

    @override
    async def execute(
        self, data: GetUserApplicationForVacancyDTO
    ) -> ApplicationDetailViewModel:
        # TODO: PASS HERE IDENTITY PROVIDER INSTEAD OF READY USER ID FROM MIDDLEWARE
        application_view = (
            await self.application_gateway.get_user_application_view_by_vacancy_id(
                data.user_id, data.vacancy_id
            )
        )
        if not application_view:
            raise UserApplicationForVacancyNotFound(
                vacancy_id=data.vacancy_id, user_id=data.user_id
            )
        return application_view
