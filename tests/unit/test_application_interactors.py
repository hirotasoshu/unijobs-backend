from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.application.apply_for_vacancy import ApplyForVacancy, ApplyForVacancyDTO
from src.application.delete_application import DeleteApplication, DeleteApplicationDTO
from src.application.get_user_application_for_vacancy import (
    GetUserApplicationForVacancy,
    GetUserApplicationForVacancyDTO,
)
from src.application.update_application import UpdateApplication, UpdateApplicationDTO
from src.application.view_models.application import ApplicationDetailViewModel
from src.application.view_models.employer import EmployerViewModel
from src.application.view_models.vacancy import VacancyViewModel
from src.domain.entity.application import Application
from src.domain.exception.application import (
    AnotherStudentCantChangeApplication,
    StudentCantChangeViewedApplication,
    UserApplicationForVacancyAlreadyExists,
    UserApplicationForVacancyNotFound,
)
from src.domain.value_object.application_status import ApplicationStatus
from src.domain.value_object.ids import EmployerId, UserId, VacancyId


pytestmark = pytest.mark.unit


class FakeTransactionManager:
    def __init__(self):
        self.commits = 0

    async def commit(self):
        self.commits += 1


class FakeApplicationGateway:
    def __init__(self):
        self.applications: list[Application] = []
        self.application_view: ApplicationDetailViewModel | None = None
        self.updated: Application | None = None
        self.deleted: Application | None = None

    async def get_by_id(self, application_id):
        return next(
            (application for application in self.applications if application.id == application_id),
            None,
        )

    async def get_user_application_by_vacancy_id(self, user_id, vacancy_id):
        return next(
            (
                application
                for application in self.applications
                if application.user_id == user_id and application.vacancy_id == vacancy_id
            ),
            None,
        )

    async def get_user_application_view_by_vacancy_id(
        self, user_id, vacancy_id, language
    ):
        return self.application_view

    async def add(self, application):
        self.applications.append(application)

    async def update(self, application):
        self.updated = application

    async def delete(self, application):
        self.deleted = application


def _user_id() -> UserId:
    return UserId(uuid4())


def _vacancy_id() -> VacancyId:
    return VacancyId(uuid4())


def _application(user_id: UserId | None = None) -> Application:
    return Application(
        user_id=user_id or _user_id(),
        vacancy_id=_vacancy_id(),
        cover_letter="Initial cover letter",
    )


def _application_view(user_id: UserId, vacancy_id: VacancyId):
    return ApplicationDetailViewModel(
        id=uuid4(),
        user_id=user_id,
        vacancy=VacancyViewModel(
            id=vacancy_id,
            title="Backend intern",
            salary_from=100,
            salary_to=200,
            employer=EmployerViewModel(
                id=EmployerId(uuid4()), name="UniJobs", avatar_url=None
            ),
        ),
        status=ApplicationStatus.PENDING,
        created_at=datetime.now(tz=UTC),
        cover_letter="Cover letter",
    )


@pytest.mark.asyncio
async def test_apply_for_vacancy_adds_application_and_commits():
    gateway = FakeApplicationGateway()
    transaction_manager = FakeTransactionManager()
    interactor = ApplyForVacancy(transaction_manager, gateway)
    user_id = _user_id()
    vacancy_id = _vacancy_id()

    application_id = await interactor.execute(
        ApplyForVacancyDTO(
            user_id=user_id, vacancy_id=vacancy_id, cover_letter="I am interested"
        )
    )

    assert gateway.applications[0].id == application_id
    assert gateway.applications[0].user_id == user_id
    assert gateway.applications[0].vacancy_id == vacancy_id
    assert transaction_manager.commits == 1


@pytest.mark.asyncio
async def test_apply_for_vacancy_rejects_duplicate_application():
    existing = _application()
    gateway = FakeApplicationGateway()
    gateway.applications.append(existing)
    transaction_manager = FakeTransactionManager()
    interactor = ApplyForVacancy(transaction_manager, gateway)

    with pytest.raises(UserApplicationForVacancyAlreadyExists):
        await interactor.execute(
            ApplyForVacancyDTO(
                user_id=existing.user_id,
                vacancy_id=existing.vacancy_id,
                cover_letter="Duplicate",
            )
        )

    assert transaction_manager.commits == 0


@pytest.mark.asyncio
async def test_update_application_updates_pending_owner_application_and_commits():
    application = _application()
    gateway = FakeApplicationGateway()
    gateway.applications.append(application)
    transaction_manager = FakeTransactionManager()
    interactor = UpdateApplication(transaction_manager, gateway)

    application_id = await interactor.execute(
        UpdateApplicationDTO(
            application_id=application.id,
            user_id=application.user_id,
            new_cover_letter="Updated cover letter",
        )
    )

    assert application_id == application.id
    assert gateway.updated is application
    assert application.cover_letter == "Updated cover letter"
    assert transaction_manager.commits == 1


@pytest.mark.asyncio
async def test_update_application_rejects_another_user_application():
    application = _application()
    gateway = FakeApplicationGateway()
    gateway.applications.append(application)
    transaction_manager = FakeTransactionManager()
    interactor = UpdateApplication(transaction_manager, gateway)

    with pytest.raises(AnotherStudentCantChangeApplication):
        await interactor.execute(
            UpdateApplicationDTO(
                application_id=application.id,
                user_id=_user_id(),
                new_cover_letter="Updated cover letter",
            )
        )

    assert gateway.updated is None
    assert transaction_manager.commits == 0


@pytest.mark.asyncio
async def test_delete_application_rejects_viewed_application():
    application = _application()
    application.status = ApplicationStatus.REVIEW
    gateway = FakeApplicationGateway()
    gateway.applications.append(application)
    transaction_manager = FakeTransactionManager()
    interactor = DeleteApplication(transaction_manager, gateway)

    with pytest.raises(StudentCantChangeViewedApplication):
        await interactor.execute(
            DeleteApplicationDTO(application_id=application.id, user_id=application.user_id)
        )

    assert gateway.deleted is None
    assert transaction_manager.commits == 0


@pytest.mark.asyncio
async def test_get_user_application_for_vacancy_returns_existing_view():
    user_id = _user_id()
    vacancy_id = _vacancy_id()
    gateway = FakeApplicationGateway()
    gateway.application_view = _application_view(user_id, vacancy_id)
    interactor = GetUserApplicationForVacancy(gateway)

    application = await interactor.execute(
        GetUserApplicationForVacancyDTO(user_id=user_id, vacancy_id=vacancy_id)
    )

    assert application is gateway.application_view


@pytest.mark.asyncio
async def test_get_user_application_for_vacancy_raises_when_missing():
    user_id = _user_id()
    vacancy_id = _vacancy_id()
    interactor = GetUserApplicationForVacancy(FakeApplicationGateway())

    with pytest.raises(UserApplicationForVacancyNotFound):
        await interactor.execute(
            GetUserApplicationForVacancyDTO(user_id=user_id, vacancy_id=vacancy_id)
        )
