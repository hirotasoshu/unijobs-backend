from src.domain.value_object.language import Language


class BaseException(Exception):
    type: str = ""
    title_en: str = ""
    title_ru: str = ""
    title_fr: str = ""

    def get_title(self, language: Language) -> str:
        match language:
            case Language.RU:
                return self.title_ru
            case Language.FR:
                return self.title_fr
            case _:
                return self.title_en

    def get_detail_msg(self, language: Language) -> str:
        match language:
            case Language.RU:
                return self._get_detail_msg_ru()
            case Language.FR:
                return self._get_detail_msg_fr()
            case _:
                return self._get_detail_msg_en()

    def _get_detail_msg_ru(self) -> str:
        raise NotImplementedError

    def _get_detail_msg_en(self) -> str:
        raise NotImplementedError

    def _get_detail_msg_fr(self) -> str:
        raise NotImplementedError
