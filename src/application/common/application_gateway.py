from typing import Protocol

from src.application.view_models.application import (
    ApplicationDetailViewModel,
    ApplicationViewModel,
)
from src.domain.entity.application import Application
from src.domain.value_object.ids import ApplicationId, UserId, VacancyId


class ApplicationViewReader(Protocol):
    async def get_user_application_views(
        self, user_id: UserId, page: int = 1, page_size: int = 10
    ) -> list[ApplicationViewModel]:
        raise NotImplementedError

    async def get_user_application_view_by_vacancy_id(
        self, user_id: UserId, vacancy_id: VacancyId
    ) -> ApplicationDetailViewModel | None:
        raise NotImplementedError


class ApplicationReader(Protocol):
    async def get_by_id(self, application_id: ApplicationId) -> Application:
        raise NotImplementedError

    async def count_user_applications(self, user_id: UserId) -> int:
        raise NotImplementedError

    async def get_user_application_by_vacancy_id(
        self, user_id: UserId, vacancy_id: VacancyId
    ) -> ApplicationDetailViewModel | None:
        raise NotImplementedError


class ApplicationWriter(Protocol):
    async def add(self, application: Application) -> None:
        """
        Apply for vacancy
        """
        raise NotImplementedError

    async def update(self, application: Application) -> None:
        """
        Update application (probably upsert)
        """
        raise NotImplementedError

    async def delete(self, application: Application) -> None:
        raise NotImplementedError
