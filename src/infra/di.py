from collections.abc import AsyncIterator

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.application.apply_for_vacancy import ApplyForVacancy
from src.application.get_employer_by_id import GetEmployerById
from src.application.get_user_application_for_vacancy import (
    GetUserApplicationForVacancy,
)
from src.application.get_user_applications import GetUserApplications
from src.application.get_vacancies_by_filters import GetVacanciesByFilters
from src.application.get_vacancy_by_id import GetVacancyById
from src.application.update_application import UpdateApplication
from src.infra.adapters.database.application_gateway import SqlAlchemyApplicationGateway
from src.infra.adapters.database.employer_gateway import SqlAlchemyEmployerGateway
from src.infra.adapters.database.transaction import SqlAlchemyTransactionManager
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
    async def provide_application_gateway(
        self, session: AsyncSession
    ) -> SqlAlchemyApplicationGateway:
        return SqlAlchemyApplicationGateway(session)

    @provide(scope=Scope.REQUEST)
    async def provide_transaction_manager(
        self, session: AsyncSession
    ) -> SqlAlchemyTransactionManager:
        return SqlAlchemyTransactionManager(session)

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

    @provide(scope=Scope.REQUEST)
    async def provide_get_user_applications_interactor(
        self, gateway: SqlAlchemyApplicationGateway
    ) -> GetUserApplications:
        return GetUserApplications(gateway)

    @provide(scope=Scope.REQUEST)
    async def provide_get_user_application_for_interactor(
        self, gateway: SqlAlchemyApplicationGateway
    ) -> GetUserApplicationForVacancy:
        return GetUserApplicationForVacancy(gateway)

    @provide(scope=Scope.REQUEST)
    async def provide_apply_for_vacancy_interactor(
        self,
        gateway: SqlAlchemyApplicationGateway,
        transaction_manager: SqlAlchemyTransactionManager,
    ) -> ApplyForVacancy:
        return ApplyForVacancy(
            application_gateway=gateway, transaction_manager=transaction_manager
        )

    @provide(scope=Scope.REQUEST)
    async def provide_update_application_interactor(
        self,
        gateway: SqlAlchemyApplicationGateway,
        transaction_manager: SqlAlchemyTransactionManager,
    ) -> UpdateApplication:
        return UpdateApplication(
            application_gateway=gateway, transaction_manager=transaction_manager
        )


def get_di_container() -> AsyncContainer:
    return make_async_container(DiProvider())
