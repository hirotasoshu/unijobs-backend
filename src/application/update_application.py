import logging
from dataclasses import dataclass
from typing import Protocol, override

from src.application.common.application_gateway import (
    ApplicationReader,
    ApplicationWriter,
)
from src.application.common.interactor import Interactor
from src.application.common.transaction import TransactionManager
from src.domain.exception.application import (
    ApplicationNotFound,
    AnotherStudentCantChangeApplication,
    StudentCantChangeViewedApplication,
)
from src.domain.value_object.ids import UserId, ApplicationId


logger = logging.getLogger("unijobs.application")


@dataclass
class UpdateApplicationDTO:
    application_id: ApplicationId
    new_cover_letter: str
    user_id: UserId


class ApplicationGateway(ApplicationReader, ApplicationWriter, Protocol):
    pass


class UpdateApplication(Interactor[UpdateApplicationDTO, ApplicationId]):
    def __init__(
        self,
        transaction_manager: TransactionManager,
        application_gateway: ApplicationGateway,
    ):
        self.transaction_manager: TransactionManager = transaction_manager
        self.application_gateway: ApplicationGateway = application_gateway

    @override
    async def execute(self, data: UpdateApplicationDTO) -> ApplicationId:
        # TODO: PASS HERE IDENTITY PROVIDER INSTEAD OF READY USER ID FROM MIDDLEWARE
        # TODO: SPLIT LOGIC FOR DIFFERENT ROLES WHEN WE HAVE THEM
        application = await self.application_gateway.get_by_id(data.application_id)
        if not application:
            logger.warning(
                "Application update rejected: application not found application_id=%s user_id=%s",
                data.application_id,
                data.user_id,
            )
            raise ApplicationNotFound(application_id=data.application_id)
        if application.user_id != data.user_id:
            logger.warning(
                "Application update rejected: forbidden application_id=%s user_id=%s owner_user_id=%s",
                data.application_id,
                data.user_id,
                application.user_id,
            )
            raise AnotherStudentCantChangeApplication(
                application_id=data.application_id, user_id=data.user_id
            )
        if not application.is_pending:
            logger.warning(
                "Application update rejected: not pending application_id=%s user_id=%s status=%s",
                data.application_id,
                data.user_id,
                application.status,
            )
            raise StudentCantChangeViewedApplication(application_id=data.application_id)

        application.cover_letter = data.new_cover_letter

        await self.application_gateway.update(application)
        await self.transaction_manager.commit()
        logger.info(
            "Application updated application_id=%s user_id=%s",
            application.id,
            data.user_id,
        )
        return application.id
