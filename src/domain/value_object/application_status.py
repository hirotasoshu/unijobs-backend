from enum import StrEnum, auto


class ApplicationStatus(StrEnum):
    PENDING = auto()
    REVIEW = auto()
    ACCEPTED = auto()
    REJECTED = auto()
