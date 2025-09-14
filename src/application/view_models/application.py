from dataclasses import dataclass
from datetime import datetime

from src.application.view_models.vacancy import VacancyViewModel
from src.domain.value_object.application_status import ApplicationStatus
from src.domain.value_object.ids import ApplicationId, UserId


@dataclass(kw_only=True)
class ApplicationViewModel:
    id: ApplicationId
    user_id: UserId
    vacancy: VacancyViewModel
    status: ApplicationStatus
    created_at: datetime


@dataclass(kw_only=True)
class ApplicationDetailViewModel(ApplicationViewModel):
    cover_letter: str
