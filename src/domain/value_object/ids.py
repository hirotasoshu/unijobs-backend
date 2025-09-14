from typing import NewType
from uuid import UUID

UserId = NewType("UserId", UUID)
VacancyId = NewType("VacancyId", UUID)
EmployerId = NewType("EmployerId", UUID)
ApplicationId = NewType("ApplicationId", UUID)
