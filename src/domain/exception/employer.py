from src.domain.value_object.ids import EmployerId


class EmployerNotFoundError(Exception):
    def __init__(self, employer_id: EmployerId) -> None:
        super().__init__(f"There is no employer with id {employer_id}!")
        self.employer_id: EmployerId = employer_id
