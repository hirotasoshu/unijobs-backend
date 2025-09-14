from dataclasses import dataclass

from src.domain.value_object.ids import EmployerId


@dataclass(kw_only=True)
class EmployerViewModel:
    id: EmployerId
    name: str
    avatar_url: str | None


@dataclass(kw_only=True)
class EmployerDetailViewModel(EmployerViewModel):
    description: str | None
