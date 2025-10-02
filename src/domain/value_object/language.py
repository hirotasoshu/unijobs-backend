from enum import StrEnum, auto
from typing import override
import re


class Language(StrEnum):
    RU = auto()
    EN = auto()
    FR = auto()

    @classmethod
    @override
    def _missing_(cls, value: object) -> "Language":
        if value is None or not isinstance(value, str):
            return cls.EN

        str_value = str(value).strip().lower()

        if "-" in str_value or "_" in str_value:
            lang_part = re.split(r"[-_]", str_value)[0]
            str_value = lang_part

        for member in cls:
            if member.value == str_value:
                return member

        return cls.EN
