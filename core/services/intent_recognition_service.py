from abc import ABC, abstractmethod
from typing import Any
from dataclasses import dataclass

from core.types.intents import Intent

@dataclass(frozen=True)
class IntentRecognitionResponse:
    intent: Intent
    session_state: Any | None


class IntentRecognitionService(ABC):

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def recognize_intent(self, text: str, session_id: str, session_state: Any | None) -> IntentRecognitionResponse:
        pass
