from typing import Protocol

from src.application.view_models.employer import EmployerDetailViewModel
from src.domain.value_object.ids import EmployerId


class EmployerViewReader(Protocol):
    async def get_view_by_id(self, id: EmployerId) -> EmployerDetailViewModel | None:
        raise NotImplementedError
