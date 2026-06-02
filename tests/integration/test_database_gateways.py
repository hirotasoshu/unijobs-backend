from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.domain.entity.application import Application
from src.domain.value_object.application_status import ApplicationStatus
from src.domain.value_object.employment_type import EmploymentType
from src.domain.value_object.ids import EmployerId, UserId, VacancyId
from src.domain.value_object.language import Language
from src.domain.value_object.workformat import WorkFormat
from src.infra.adapters.database.application_gateway import SqlAlchemyApplicationGateway
from src.infra.adapters.database.employer_gateway import SqlAlchemyEmployerGateway
from src.infra.adapters.database.models import EmployerModel, VacancyModel
from src.infra.adapters.database.vacancy_gateway import SqlAlchemyVacancyGateway


pytestmark = pytest.mark.integration


def _employer_model() -> EmployerModel:
    return EmployerModel(
        id=EmployerId(uuid4()),
        avatar_url="https://example.com/avatar.png",
        name_en="Acme",
        name_ru="Акме",
        name_fr="Acmé",
        description_en="English description",
        description_ru="Русское описание",
        description_fr="Description française",
    )


def _vacancy_model(employer_id: EmployerId) -> VacancyModel:
    return VacancyModel(
        id=VacancyId(uuid4()),
        title_en="Backend intern",
        title_ru="Бэкенд стажер",
        title_fr="Stagiaire backend",
        description_en="Build APIs",
        description_ru="Разработка API",
        description_fr="Construire des API",
        location_en="Remote",
        location_ru="Удаленно",
        location_fr="À distance",
        salary_from=100,
        salary_to=200,
        work_format=WorkFormat.REMOTE,
        employment_type=EmploymentType.INTERNSHIP,
        key_skills="python, fastapi, ydb",
        employer_id=employer_id,
    )


async def _seed_vacancy(db_session):
    employer = _employer_model()
    vacancy = _vacancy_model(employer.id)
    db_session.add_all([employer, vacancy])
    await db_session.commit()
    return employer, vacancy


@pytest.mark.asyncio
async def test_employer_gateway_returns_localized_view(db_session):
    employer, _ = await _seed_vacancy(db_session)
    gateway = SqlAlchemyEmployerGateway(db_session)

    view = await gateway.get_view_by_id(employer.id, Language.RU)

    assert view is not None
    assert view.id == employer.id
    assert view.name == "Акме"
    assert view.description == "Русское описание"


@pytest.mark.asyncio
async def test_vacancy_gateway_filters_and_returns_localized_detail(db_session):
    employer, vacancy = await _seed_vacancy(db_session)
    gateway = SqlAlchemyVacancyGateway(db_session)

    count = await gateway.count_by_filters(search="backend", employer_id=employer.id)
    views = await gateway.get_views_by_filters(search="backend", language=Language.FR)
    detail = await gateway.get_view_by_id(vacancy.id, language=Language.EN)

    assert count == 1
    assert len(views) == 1
    assert views[0].title == "Stagiaire backend"
    assert views[0].employer.name == "Acmé"
    assert detail is not None
    assert detail.id == vacancy.id
    assert detail.key_skills == ["python", "fastapi", "ydb"]
    assert detail.location == "Remote"


@pytest.mark.asyncio
async def test_application_gateway_adds_reads_updates_deletes_application(db_session):
    _, vacancy = await _seed_vacancy(db_session)
    gateway = SqlAlchemyApplicationGateway(db_session)
    user_id = UserId(uuid4())
    application = Application(
        user_id=user_id,
        vacancy_id=vacancy.id,
        cover_letter="Initial cover letter",
        created_at=datetime.now(tz=UTC),
    )

    await gateway.add(application)
    await db_session.commit()

    stored = await gateway.get_by_id(application.id)
    duplicate = await gateway.get_user_application_by_vacancy_id(user_id, vacancy.id)
    views = await gateway.get_user_application_views(user_id, language=Language.EN)
    detail = await gateway.get_user_application_view_by_vacancy_id(
        user_id, vacancy.id, language=Language.EN
    )
    count = await gateway.count_user_applications(user_id)

    assert stored is not None
    assert stored.cover_letter == "Initial cover letter"
    assert duplicate is not None
    assert duplicate.id == application.id
    assert len(views) == 1
    assert views[0].vacancy.title == "Backend intern"
    assert detail is not None
    assert detail.cover_letter == "Initial cover letter"
    assert count == 1

    application.cover_letter = "Updated cover letter"
    application.status = ApplicationStatus.REVIEW
    await gateway.update(application)
    await db_session.commit()

    updated = await gateway.get_by_id(application.id)
    assert updated is not None
    assert updated.cover_letter == "Updated cover letter"
    assert updated.status == ApplicationStatus.REVIEW

    await gateway.delete(application)
    await db_session.commit()

    assert await gateway.get_by_id(application.id) is None
