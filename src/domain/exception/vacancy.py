from src.domain.value_object.ids import VacancyId


class VacancyNotFoundError(Exception):
    def __init__(self, vacancy_id: VacancyId) -> None:
        super().__init__(f"There is no vacancy with id {vacancy_id}!")
        self.vacancy_id: VacancyId = vacancy_id
