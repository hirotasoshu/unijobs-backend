from dataclasses import dataclass
from typing import Protocol, override

from src.application.common.employer_gateway import EmployerViewReader
from src.application.common.interactor import Interactor
from src.application.view_models.employer import EmployerDetailViewModel
from src.domain.value_object.ids import EmployerId
from src.domain.exception.employer import EmployerNotFoundError


@dataclass
class GetEmployerByIdDTO:
    employer_id: EmployerId


class EmployerGateway(EmployerViewReader, Protocol):
    pass


class GetEmployerById(Interactor[GetEmployerByIdDTO, EmployerDetailViewModel]):
    def __init__(self, employer_gateway: EmployerGateway):
        self.employer_gateway: EmployerGateway = employer_gateway

    @override
    async def execute(self, data: GetEmployerByIdDTO) -> EmployerDetailViewModel:
        employer_view = await self.employer_gateway.get_view_by_id(data.employer_id)
        if not employer_view:
            raise EmployerNotFoundError(data.employer_id)
        return employer_view
