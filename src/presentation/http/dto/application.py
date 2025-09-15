from pydantic import BaseModel

from src.domain.value_object.ids import VacancyId


class CreateApplicationRequest(BaseModel):
    cover_letter: str
    vacancy_id: VacancyId


class UpdateApplicationRequest(BaseModel):
    cover_letter: str
