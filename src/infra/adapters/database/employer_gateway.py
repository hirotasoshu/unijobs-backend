from typing import override
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.view_models.employer import (
    EmployerDetailViewModel,
)
from src.application.common.employer_gateway import EmployerViewReader
from src.domain.value_object.ids import EmployerId
from src.infra.adapters.database.models import EmployerModel


class SqlAlchemyEmployerGateway(EmployerViewReader):
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    @override
    async def get_view_by_id(self, id: EmployerId) -> EmployerDetailViewModel | None:
        stmt = select(EmployerModel).where(EmployerModel.id == id)
        res = await self.session.execute(stmt)
        employer_db_model = res.scalar_one_or_none()
        if employer_db_model is None:
            return None
        return EmployerDetailViewModel(
            id=employer_db_model.id,
            name=employer_db_model.name,
            avatar_url=employer_db_model.avatar_url,
            description=employer_db_model.description,
        )
