from collections.abc import Sequence
from typing import override

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.application.common.vacancy_gateway import VacancyReader, VacancyViewReader
from src.application.view_models.employer import EmployerViewModel
from src.application.view_models.vacancy import VacancyDetailViewModel, VacancyViewModel
from src.domain.value_object.employment_type import EmploymentType
from src.domain.value_object.ids import EmployerId, VacancyId
from src.domain.value_object.workformat import WorkFormat
from src.infra.adapters.database.models import EmployerModel, VacancyModel


class SqlAlchemyVacancyGateway(VacancyReader, VacancyViewReader):
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    @staticmethod
    def _parse_key_skills(raw: str | None) -> list[str]:
        if not raw:
            return []
        return [s.strip() for s in raw.split(",") if s.strip()]

    def _apply_filters_to_stmt(
        self,
        stmt,
        search: str | None = None,
        salary_from: int | None = None,
        work_format: WorkFormat | None = None,
        employment_type: EmploymentType | None = None,
        employer_id: EmployerId | None = None,
    ):
        # NOTE: мы предполагаем, что join(EmployerModel) уже применён там, где нужно
        if search:
            term = f"%{search}%"
            stmt = stmt.where(
                or_(
                    VacancyModel.title.ilike(term),
                    EmployerModel.name.ilike(term),
                    VacancyModel.key_skills.ilike(term),
                )
            )

        if salary_from is not None:
            stmt = stmt.where(VacancyModel.salary_from >= salary_from)
        if work_format is not None:
            stmt = stmt.where(VacancyModel.work_format == work_format)
        if employment_type is not None:
            stmt = stmt.where(VacancyModel.employment_type == employment_type)
        if employer_id is not None:
            stmt = stmt.where(VacancyModel.employer_id == employer_id)

        return stmt

    @override
    async def count_by_filters(
        self,
        search: str | None = None,
        salary_from: int | None = None,
        work_format: WorkFormat | None = None,
        employment_type: EmploymentType | None = None,
        employer_id: EmployerId | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(VacancyModel).join(EmployerModel)
        stmt = self._apply_filters_to_stmt(
            stmt, search, salary_from, work_format, employment_type, employer_id
        )
        res = await self.session.execute(stmt)
        return int(res.scalar_one())

    @override
    async def get_views_by_filters(
        self,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
        salary_from: int | None = None,
        work_format: WorkFormat | None = None,
        employment_type: EmploymentType | None = None,
        employer_id: EmployerId | None = None,
    ) -> list[VacancyViewModel]:
        stmt = select(VacancyModel).options(joinedload(VacancyModel.employer))
        stmt = self._apply_filters_to_stmt(
            stmt, search, salary_from, work_format, employment_type, employer_id
        )

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        res = await self.session.execute(stmt)
        rows: Sequence[VacancyModel] = res.scalars().all()

        result: list[VacancyViewModel] = []
        for vacancy_db_model in rows:
            emp_vm = EmployerViewModel(
                id=vacancy_db_model.employer.id,
                name=vacancy_db_model.employer.name,
                avatar_url=vacancy_db_model.employer.avatar_url,
            )
            vacancy_vm = VacancyViewModel(
                id=vacancy_db_model.id,
                title=vacancy_db_model.title,
                salary_from=vacancy_db_model.salary_from,
                salary_to=vacancy_db_model.salary_to,
                employer=emp_vm,
            )
            result.append(vacancy_vm)

        return result

    @override
    async def get_view_by_id(self, id: VacancyId) -> VacancyDetailViewModel | None:
        stmt = (
            select(VacancyModel)
            .options(joinedload(VacancyModel.employer))
            .where(VacancyModel.id == id)
        )
        res = await self.session.execute(stmt)
        vacancy_db_model = res.scalar_one_or_none()
        if vacancy_db_model is None:
            return None

        employer_view_model = EmployerViewModel(
            id=vacancy_db_model.employer.id,
            name=vacancy_db_model.employer.name,
            avatar_url=vacancy_db_model.employer.avatar_url,
        )

        return VacancyDetailViewModel(
            id=vacancy_db_model.id,
            title=vacancy_db_model.title,
            salary_from=vacancy_db_model.salary_from,
            salary_to=vacancy_db_model.salary_to,
            employer=employer_view_model,
            key_skills=self._parse_key_skills(vacancy_db_model.key_skills),
            work_format=vacancy_db_model.work_format,
            employment_type=vacancy_db_model.employment_type,
            description=vacancy_db_model.description,
            location=vacancy_db_model.location,
        )
