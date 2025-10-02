from collections.abc import Sequence
from typing import override

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.application.common.application_gateway import (
    ApplicationReader,
    ApplicationViewReader,
    ApplicationWriter,
)
from src.application.view_models.application import (
    ApplicationDetailViewModel,
    ApplicationViewModel,
)
from src.application.view_models.employer import EmployerViewModel
from src.application.view_models.vacancy import VacancyViewModel
from src.domain.entity.application import Application
from src.domain.value_object.ids import ApplicationId, UserId, VacancyId
from src.domain.value_object.language import Language
from src.infra.adapters.database.models import ApplicationModel, VacancyModel


class SqlAlchemyApplicationGateway(
    ApplicationViewReader, ApplicationReader, ApplicationWriter
):
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    @override
    async def get_user_application_views(
        self,
        user_id: UserId,
        page: int = 1,
        page_size: int = 10,
        language: Language = Language.EN,
    ) -> list[ApplicationViewModel]:
        stmt = (
            select(ApplicationModel)
            .options(
                joinedload(ApplicationModel.vacancy).joinedload(VacancyModel.employer)
            )
            .distinct()
            .where(ApplicationModel.user_id == user_id)
            .order_by(ApplicationModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        res = await self.session.execute(stmt)
        applications: Sequence[ApplicationModel] = res.scalars().all()

        result: list[ApplicationViewModel] = []
        for app_db_model in applications:
            vacancy_vm = self._create_vacancy_view_model(app_db_model.vacancy, language)

            app_vm = ApplicationViewModel(
                id=app_db_model.id,
                user_id=app_db_model.user_id,
                vacancy=vacancy_vm,
                status=app_db_model.status,
                created_at=app_db_model.created_at,
            )
            result.append(app_vm)

        return result

    @override
    async def get_user_application_view_by_vacancy_id(
        self, user_id: UserId, vacancy_id: VacancyId, language: Language = Language.EN
    ) -> ApplicationDetailViewModel | None:
        stmt = (
            select(ApplicationModel)
            .options(
                joinedload(ApplicationModel.vacancy).joinedload(VacancyModel.employer)
            )
            .where(
                ApplicationModel.user_id == user_id,
                ApplicationModel.vacancy_id == vacancy_id,
            )
        )

        res = await self.session.execute(stmt)
        app_db_model = res.scalar_one_or_none()

        if app_db_model is None:
            return None

        vacancy_vm = self._create_vacancy_view_model(app_db_model.vacancy, language)

        return ApplicationDetailViewModel(
            id=app_db_model.id,
            user_id=app_db_model.user_id,
            vacancy=vacancy_vm,
            status=app_db_model.status,
            created_at=app_db_model.created_at,
            cover_letter=app_db_model.cover_letter,
        )

    @override
    async def get_by_id(self, application_id: ApplicationId) -> Application | None:
        stmt = select(ApplicationModel).where(ApplicationModel.id == application_id)
        res = await self.session.execute(stmt)
        app_db_model = res.scalar_one_or_none()

        if app_db_model is None:
            return None

        return self._to_domain_entity(app_db_model)

    @override
    async def count_user_applications(self, user_id: UserId) -> int:
        stmt = (
            select(func.count())
            .select_from(ApplicationModel)
            .where(ApplicationModel.user_id == user_id)
        )
        res = await self.session.execute(stmt)
        return int(res.scalar_one())

    @override
    async def get_user_application_by_vacancy_id(
        self, user_id: UserId, vacancy_id: VacancyId
    ) -> Application | None:
        stmt = select(ApplicationModel).where(
            ApplicationModel.user_id == user_id,
            ApplicationModel.vacancy_id == vacancy_id,
        )

        res = await self.session.execute(stmt)
        app_db_model = res.scalar_one_or_none()

        if app_db_model is None:
            return None

        return self._to_domain_entity(app_db_model)

    @override
    async def add(self, application: Application) -> None:
        app_db_model = self._to_db_model(application)
        self.session.add(app_db_model)

    @override
    async def update(self, application: Application) -> None:
        app_db_model = self._to_db_model(application)
        _ = await self.session.merge(app_db_model)

    @override
    async def delete(self, application: Application) -> None:
        stmt = delete(ApplicationModel).where(ApplicationModel.id == application.id)
        _ = await self.session.execute(stmt)

    def _to_db_model(self, application: Application) -> ApplicationModel:
        return ApplicationModel(
            id=application.id,
            user_id=application.user_id,
            vacancy_id=application.vacancy_id,
            cover_letter=application.cover_letter,
            status=application.status,
            created_at=application.created_at,
        )

    def _create_vacancy_view_model(
        self, vacancy_db_model: VacancyModel, language: Language
    ) -> VacancyViewModel:
        employer_vm = EmployerViewModel(
            id=vacancy_db_model.employer.id,
            name=vacancy_db_model.employer.name.get(language),
            avatar_url=vacancy_db_model.employer.avatar_url,
        )

        return VacancyViewModel(
            id=vacancy_db_model.id,
            title=vacancy_db_model.title.get(language),
            salary_from=vacancy_db_model.salary_from,
            salary_to=vacancy_db_model.salary_to,
            employer=employer_vm,
        )

    def _to_domain_entity(self, app_db_model: ApplicationModel) -> Application:
        return Application(
            id=app_db_model.id,
            user_id=app_db_model.user_id,
            vacancy_id=app_db_model.vacancy_id,
            cover_letter=app_db_model.cover_letter,
            status=app_db_model.status,
            created_at=app_db_model.created_at,
        )
