from typing import override

from src.domain.value_object.ids import EmployerId

from .base import BaseException


class EmployerNotFoundError(BaseException):
    type: str = "EmployerNotFound"
    title_en: str = "Employer not found"
    title_ru: str = "Работодатель не найден"
    title_fr: str = "Employeur non trouvée"

    def __init__(self, employer_id: EmployerId) -> None:
        self.employer_id: EmployerId = employer_id
        super().__init__(self._get_detail_msg_en())

    @override
    def _get_detail_msg_en(self) -> str:
        return f"There is no employer with id {self.employer_id}!"

    @override
    def _get_detail_msg_ru(self) -> str:
        return f"Работодатель с id {self.employer_id} не найдена!"

    @override
    def _get_detail_msg_fr(self) -> str:
        return f"Employeur avec l'id {self.employer_id} introuvable!"
