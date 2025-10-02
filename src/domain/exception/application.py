from typing import override

from src.domain.value_object.ids import ApplicationId, UserId, VacancyId

from .base import BaseException


class UserApplicationForVacancyNotFound(BaseException):
    type: str = "UserApplicationForVacancyNotFound"
    title_en: str = "User application for vacancy not found"
    title_ru: str = "Отклик пользователя на вакансию не найден"
    title_fr: str = "Candidature de l'utilisateur pour un poste vacant introuvable"

    def __init__(self, vacancy_id: VacancyId, user_id: UserId) -> None:
        self.vacancy_id: VacancyId = vacancy_id
        self.user_id: UserId = user_id
        super().__init__(self._get_detail_msg_en())

    @override
    def _get_detail_msg_en(self) -> str:
        return f"There is no application for vacancy {self.vacancy_id} from user {self.user_id}!"

    @override
    def _get_detail_msg_ru(self) -> str:
        return f"Отклик пользователя {self.user_id} на вакансию {self.vacancy_id} не найден!"

    @override
    def _get_detail_msg_fr(self) -> str:
        return f"Il n'y a pas de candidature pour l'offre d'emploi {self.vacancy_id} de la part de l'utilisateur {self.user_id}"


class UserApplicationForVacancyAlreadyExists(BaseException):
    type: str = "ApplicationAlreadyExists"
    title_en: str = "Application for vacancy already exists"
    title_ru: str = "Отклик на вакансию уже существует"
    title_fr: str = "Candidature pour l'offre d'emploi existe deja"

    def __init__(self, vacancy_id: VacancyId, user_id: UserId) -> None:
        super().__init__(self._get_detail_msg_en())
        self.vacancy_id: VacancyId = vacancy_id
        self.user_id: UserId = user_id

    @override
    def _get_detail_msg_en(self) -> str:
        return f"Application for vacancy {self.vacancy_id} from user {self.user_id} already exists!"

    @override
    def _get_detail_msg_ru(self) -> str:
        return f"Отклик пользователя {self.user_id} на вакансию {self.vacancy_id} уже существует!"

    @override
    def _get_detail_msg_fr(self) -> str:
        return f"Une candidature pour l'offre d'emploi {self.vacancy_id} de la part de l'utilisateur {self.user_id} a deja ete creee!"


class ApplicationNotFound(BaseException):
    type: str = "ApplicationNotFound"
    title_en: str = "Application not found"
    title_ru: str = "Отклик не найден"
    title_fr: str = "Candidature introuvable"

    def __init__(self, application_id: ApplicationId) -> None:
        self.application_id: ApplicationId = application_id
        super().__init__(self._get_detail_msg_en())

    @override
    def _get_detail_msg_en(self) -> str:
        return f"Application with id {self.application_id} not found!"

    @override
    def _get_detail_msg_ru(self) -> str:
        return f"Отклик с id {self.application_id} не был найден!"

    @override
    def _get_detail_msg_fr(self) -> str:
        return f"La candidature avec l'id {self.application_id} n'a pas été trouvée!"


class AnotherStudentCantChangeApplication(BaseException):
    type: str = "AnotherStudentCantChangeApplication"
    title_en: str = "Student can't change other person's application"
    title_ru: str = "Студент не может изменить отклик другого студента"
    title_fr: str = (
        "Le stagiaire ne peut pas modifier la candidature d'un autre stagiaire"
    )

    def __init__(self, application_id: ApplicationId, user_id: UserId) -> None:
        self.application_id: ApplicationId = application_id
        self.user_id: UserId = user_id
        super().__init__(self._get_detail_msg_en())

    @override
    def _get_detail_msg_en(self) -> str:
        return f"Student {self.user_id} can't change application with id {self.application_id}!"

    @override
    def _get_detail_msg_ru(self) -> str:
        return f"Студент {self.user_id} не может изменить отклик {self.application_id}!"

    @override
    def _get_detail_msg_fr(self) -> str:
        return f"Le stagiaire {self.user_id} ne peut pas modifier la candidature {self.application_id}!"


class StudentCantChangeViewedApplication(BaseException):
    type: str = "CantChangeViewedApplication"
    title_en: str = "Student can't change viewed application"
    title_ru: str = "Студент не может изменить просмотренный работодателем отклик"
    title_fr: str = (
        "Le stagiaire ne peut pas modifier une candidature vue par l'employeur"
    )

    def __init__(self, application_id: ApplicationId) -> None:
        self.application_id: ApplicationId = application_id
        super().__init__(self._get_detail_msg_en())

    @override
    def _get_detail_msg_en(self) -> str:
        return f"Application with id {self.application_id} is already viewed!"

    @override
    def _get_detail_msg_ru(self) -> str:
        return f"Отклик с id {self.application_id} уже был просмотрен!"

    @override
    def _get_detail_msg_fr(self) -> str:
        return f"La candidature avec l'id {self.application_id} a deja ete vue!"
