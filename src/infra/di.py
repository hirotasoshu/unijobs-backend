from collections.abc import AsyncIterator

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.application.get_employer_by_id import GetEmployerById
from src.application.get_vacancies_by_filters import GetVacanciesByFilters
from src.application.get_vacancy_by_id import GetVacancyById
from src.infra.adapters.database.employer_gateway import SqlAlchemyEmployerGateway
from src.infra.adapters.database.vacancy_gateway import SqlAlchemyVacancyGateway


class DiProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_engine(self) -> AsyncEngine:
        return create_async_engine(
            "sqlite+aiosqlite:////home/hirotasoshu/code/unijobs-backend/test.db",
            echo=True,
        )

    @provide(scope=Scope.APP)
    async def provide_session_maker(self, engine: AsyncEngine) -> async_sessionmaker:
        return async_sessionmaker(
            engine,
            expire_on_commit=False,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
        )

    @provide(scope=Scope.REQUEST)
    async def provide_session(
        self, session_maker: async_sessionmaker
    ) -> AsyncIterator[AsyncSession]:
        session = session_maker()
        yield session
        await session.close()

    @provide(scope=Scope.REQUEST)
    async def provide_employer_gateway(
        self, session: AsyncSession
    ) -> SqlAlchemyEmployerGateway:
        return SqlAlchemyEmployerGateway(session)

    @provide(scope=Scope.REQUEST)
    async def provide_vacancy_gateway(
        self, session: AsyncSession
    ) -> SqlAlchemyVacancyGateway:
        return SqlAlchemyVacancyGateway(session)

    @provide(scope=Scope.REQUEST)
    async def provide_get_employer_by_id_interactor(
        self, gateway: SqlAlchemyEmployerGateway
    ) -> GetEmployerById:
        return GetEmployerById(gateway)

    @provide(scope=Scope.REQUEST)
    async def provide_get_vacancy_by_id_interactor(
        self, gateway: SqlAlchemyVacancyGateway
    ) -> GetVacancyById:
        return GetVacancyById(gateway)

    @provide(scope=Scope.REQUEST)
    async def provide_get_vacancies_by_filters_interactor(
        self, gateway: SqlAlchemyVacancyGateway
    ) -> GetVacanciesByFilters:
        return GetVacanciesByFilters(gateway)


def get_di_container() -> AsyncContainer:
    return make_async_container(DiProvider())
