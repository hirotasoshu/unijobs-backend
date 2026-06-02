from dataclasses import dataclass
from typing import Protocol, override

from src.application.common.application_gateway import (
    ApplicationReader,
    ApplicationWriter,
)
from src.application.common.interactor import Interactor
from src.application.common.transaction import TransactionManager
from src.domain.exception.application import (
    AnotherStudentCantChangeApplication,
    ApplicationNotFound,
    StudentCantChangeViewedApplication,
)
from src.domain.value_object.ids import ApplicationId, UserId


@dataclass
class DeleteApplicationDTO:
    application_id: ApplicationId
    user_id: UserId


class ApplicationGateway(ApplicationReader, ApplicationWriter, Protocol):
    pass


class DeleteApplication(Interactor[DeleteApplicationDTO, None]):
    def __init__(
        self,
        transaction_manager: TransactionManager,
        application_gateway: ApplicationGateway,
    ):
        self.transaction_manager = transaction_manager
        self.application_gateway = application_gateway

    @override
    async def execute(self, data: DeleteApplicationDTO) -> None:
        application = await self.application_gateway.get_by_id(data.application_id)
        if not application:
            raise ApplicationNotFound(application_id=data.application_id)
        if application.user_id != data.user_id:
            raise AnotherStudentCantChangeApplication(
                application_id=data.application_id, user_id=data.user_id
            )
        if not application.is_pending:
            raise StudentCantChangeViewedApplication(application_id=data.application_id)

        await self.application_gateway.delete(application)
        await self.transaction_manager.commit()
