from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.types.intents import Intent


@dataclass
class MedicalInfo:
    message: str

@dataclass
class MedicalInfoError(MedicalInfo):
    pass

class MedicalInfoService(ABC):

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def get_medical_info(self, intent: Intent) -> MedicalInfo:
        pass
