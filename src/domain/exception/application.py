from src.domain.value_object.ids import UserId, VacancyId, ApplicationId


class UserApplicationForVacancyNotFound(Exception):
    def __init__(self, vacancy_id: VacancyId, user_id: UserId) -> None:
        super().__init__(
            f"There is no application for vacancy {vacancy_id} from user {user_id}!"
        )
        self.vacancy_id: VacancyId = vacancy_id
        self.user_id: UserId = user_id


class UserApplicationForVacancyAlreadyExists(Exception):
    def __init__(self, vacancy_id: VacancyId, user_id: UserId) -> None:
        super().__init__(
            f"Application for vacancy {vacancy_id} from user {user_id} already exists!"
        )
        self.vacancy_id: VacancyId = vacancy_id
        self.user_id: UserId = user_id


class ApplicationNotFound(Exception):
    def __init__(self, application_id: ApplicationId) -> None:
        super().__init__(f"Application with id {application_id} not found!")
        self.application_id: ApplicationId = application_id


class AnotherStudentCantChangeApplication(Exception):
    def __init__(self, application_id: ApplicationId, user_id: UserId) -> None:
        super().__init__(
            f"Student {user_id} can't change application with id {application_id}!"
        )
        self.application_id: ApplicationId = application_id
        self.user_id: UserId = user_id


class StudentCantChangeViewedApplication(Exception):
    def __init__(self, application_id: ApplicationId) -> None:
        super().__init__(f"Application with id {application_id} is already viewed!")
        self.application_id: ApplicationId = application_id
