from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from src.domain.value_object.application_status import ApplicationStatus
from src.domain.value_object.ids import ApplicationId, UserId, VacancyId


@dataclass
class Application:
    user_id: UserId
    vacancy_id: VacancyId
    cover_letter: str
    id: ApplicationId = field(default_factory=uuid4)  # pyright: ignore [reportAssignmentType]
    status: ApplicationStatus = field(default=ApplicationStatus.PENDING)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))

    @property
    def is_pending(self):
        return self.status == ApplicationStatus.PENDING
