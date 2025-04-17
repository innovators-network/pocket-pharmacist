from abc import ABC, abstractmethod


class TranslationService(ABC):

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def translate_text(self, text: str, source_lang: str | None, target_lang: str) -> tuple[str, str, str]:
        pass
