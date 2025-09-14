from typing import override

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.common.transaction import TransactionManager


class SqlAlchemyTransactionManager(TransactionManager):
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    @override
    async def commit(self) -> None:
        await self.session.commit()

    @override
    async def flush(self) -> None:
        await self.session.flush()

    @override
    async def rollback(self) -> None:
        await self.session.rollback()
