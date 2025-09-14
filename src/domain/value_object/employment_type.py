from enum import StrEnum, auto


class EmploymentType(StrEnum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    INTERNSHIP = auto()
    TEMPORARY = auto()
