from dataclasses import dataclass
from math import ceil
from typing import Protocol, override

from src.application.common.application_gateway import (
    ApplicationReader,
    ApplicationViewReader,
)
from src.application.common.interactor import Interactor
from src.application.view_models.application import ApplicationViewModel
from src.domain.exception.pagination import IncorrectPagination
from src.domain.value_object.ids import UserId
from src.domain.value_object.language import Language


@dataclass
class UserApplicationsDTO:
    user_id: UserId
    page: int = 1
    page_size: int = 10
    language: Language = Language.EN


@dataclass
class UserApplicationResultDTO:
    total: int
    total_pages: int
    result: list[ApplicationViewModel]


class ApplicationsGateway(ApplicationReader, ApplicationViewReader, Protocol):
    pass


class GetUserApplications(Interactor[UserApplicationsDTO, UserApplicationResultDTO]):
    # TODO: PASS HERE IDENTITY PROVIDER INSTEAD OF READY USER ID FROM MIDDLEWARE
    def __init__(self, applications_gateway: ApplicationsGateway):
        self.applications_gateway: ApplicationsGateway = applications_gateway

    @override
    async def execute(self, data: UserApplicationsDTO) -> UserApplicationResultDTO:
        if data.page < 1 or data.page_size > 500:
            raise IncorrectPagination(page=data.page, page_size=data.page_size)
        total = await self.applications_gateway.count_user_applications(data.user_id)
        total_pages = ceil(total / data.page_size)
        result = await self.applications_gateway.get_user_application_views(
            user_id=data.user_id,
            page=data.page,
            page_size=data.page_size,
            language=data.language,
        )
        return UserApplicationResultDTO(
            result=result, total=total, total_pages=total_pages
        )
