from abc import ABC, abstractmethod
from typing import Dict, Any


class TranslationService(ABC):

    @abstractmethod
    def translate_text(self, text, source_lang='auto', target_lang='en') -> str | None:
        pass


class IntentRecognitionService(ABC):

    @abstractmethod
    def recognize_intent(self, text: str, session_id: str) -> Dict[str, Any]:
        pass


class MedicalInfoService(ABC):

    @abstractmethod
    def initialize(self):
        """
        Initialize the service. This can include setting up connections, loading models, etc.
        """
        pass

    @abstractmethod
    def cleanup(self):
        """

        :return:
        """
    @abstractmethod
    def get_medical_info(self, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        pass