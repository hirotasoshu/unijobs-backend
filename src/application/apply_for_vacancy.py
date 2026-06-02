import logging
from dataclasses import dataclass
from typing import Protocol, override

from src.application.common.application_gateway import (
    ApplicationReader,
    ApplicationWriter,
)
from src.application.common.interactor import Interactor
from src.application.common.transaction import TransactionManager
from src.domain.entity.application import Application
from src.domain.exception.application import UserApplicationForVacancyAlreadyExists
from src.domain.value_object.ids import UserId, VacancyId, ApplicationId


logger = logging.getLogger("unijobs.application")


@dataclass
class ApplyForVacancyDTO:
    vacancy_id: VacancyId
    user_id: UserId
    cover_letter: str


class ApplicationGateway(ApplicationReader, ApplicationWriter, Protocol):
    pass


class ApplyForVacancy(Interactor[ApplyForVacancyDTO, ApplicationId]):
    def __init__(
        self,
        transaction_manager: TransactionManager,
        application_gateway: ApplicationGateway,
    ):
        self.transaction_manager: TransactionManager = transaction_manager
        self.application_gateway: ApplicationGateway = application_gateway

    @override
    async def execute(self, data: ApplyForVacancyDTO) -> ApplicationId:
        # TODO: PASS HERE IDENTITY PROVIDER INSTEAD OF READY USER ID FROM MIDDLEWARE
        # TODO: CHECK THAT USER HAVE STUDENT ROLE WHEN WE WILL HAVE MULTIPLE ROLES
        existing_application = (
            await self.application_gateway.get_user_application_by_vacancy_id(
                user_id=data.user_id, vacancy_id=data.vacancy_id
            )
        )
        if existing_application:
            logger.warning(
                "Application creation rejected: duplicate application user_id=%s vacancy_id=%s",
                data.user_id,
                data.vacancy_id,
            )
            raise UserApplicationForVacancyAlreadyExists(
                vacancy_id=data.vacancy_id, user_id=data.user_id
            )
        application = Application(
            vacancy_id=data.vacancy_id,
            user_id=data.user_id,
            cover_letter=data.cover_letter,
        )
        await self.application_gateway.add(application)
        await self.transaction_manager.commit()
        logger.info(
            "Application created application_id=%s user_id=%s vacancy_id=%s",
            application.id,
            data.user_id,
            data.vacancy_id,
        )
        return application.id
