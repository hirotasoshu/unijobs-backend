from dataclasses import dataclass

from src.domain.value_object.ids import EmployerId


@dataclass
class Employer:
    id: EmployerId
    name: str
    avatar_url: str
    description: str
