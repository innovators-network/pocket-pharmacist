from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any

from core.types.intents import Intent

class TranslationService(ABC):

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        pass


@dataclass
class IntentRecognitionResponse:
    intent: Intent
    session_id: str = ""
    session_state: Any | None = None


class IntentRecognitionService(ABC):

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def recognize_intent(self, text: str, session_id: str, session_states: Any | None) -> IntentRecognitionResponse:
        pass


@dataclass
class MedicalInfo:
    intent: Intent
    message: str

@dataclass
class MedicalInfoError:
    error: str

MedicalInfoResponse = MedicalInfo | MedicalInfoError

class MedicalInfoService(ABC):

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def get_medical_info(self, intent: Intent) -> MedicalInfoResponse:
        pass
