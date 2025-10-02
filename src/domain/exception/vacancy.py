from typing import override

from src.domain.value_object.ids import VacancyId

from .base import BaseException


class VacancyNotFoundError(BaseException):
    type: str = "VacancyNotFound"
    title_en: str = "Vacancy not found"
    title_ru: str = "Вакансия не найдена"
    title_fr: str = "Vacance non trouvée"

    def __init__(self, vacancy_id: VacancyId) -> None:
        self.vacancy_id: VacancyId = vacancy_id
        super().__init__(self._get_detail_msg_en())

    @override
    def _get_detail_msg_en(self) -> str:
        return f"There is no vacancy with id {self.vacancy_id}!"

    @override
    def _get_detail_msg_ru(self) -> str:
        return f"Вакансия с id {self.vacancy_id} не найдена!"

    @override
    def _get_detail_msg_fr(self) -> str:
        return f"Vacance avec l'id {self.vacancy_id} introuvable!"
