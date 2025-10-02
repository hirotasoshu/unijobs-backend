from typing import override

from .base import BaseException


class IncorrectPagination(BaseException):
    type: str = "IncorrectPagination"
    title_en: str = "Incorrect pagintation params"
    title_ru: str = "Некорректные параметры пагинации"
    title_fr: str = "Paramètres de pagination incorrects"

    def __init__(self, page: int, page_size: int) -> None:
        self.page: int = page
        self.page_size: int = page_size
        super().__init__(self._get_detail_msg_en())

    @override
    def _get_detail_msg_en(self) -> str:
        return "Page must be >= 1 and page_size must be <= 500"

    @override
    def _get_detail_msg_ru(self) -> str:
        return "Page должен быть >= 1 и page_size должен быть <= 500"

    @override
    def _get_detail_msg_fr(self) -> str:
        return "La page doit être >= 1 et page_size doit être"
