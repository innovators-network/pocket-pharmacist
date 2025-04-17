from dataclasses import dataclass
from typing import Literal, get_args, ClassVar
from abc import ABC, abstractmethod

DRUG_SIDE_EFFECTS = "DrugSideEffects"
DRUG_DOSAGE = "DrugDosage"
DRUG_INTERACTIONS = "DrugInteractions"
DRUG_WARNINGS = "DrugWarnings"
DRUG_INDICATIONS_AND_USAGE = "DrugIndicationsAndUsage"

DRUG_INTENTS = [DRUG_SIDE_EFFECTS, DRUG_DOSAGE, DRUG_INTERACTIONS, DRUG_WARNINGS, DRUG_INDICATIONS_AND_USAGE]

@dataclass
class Intent(ABC):
    pass

@dataclass
class DrugIntent(Intent, ABC):
    intent_name: ClassVar[str]
    drug_name: str

@dataclass
class DrugSideEffectsIntent(DrugIntent):
    intent_name: ClassVar[str] = DRUG_SIDE_EFFECTS

@dataclass
class DrugDosageIntent(DrugIntent):
    intent_name: ClassVar[str] = DRUG_DOSAGE

@dataclass
class DrugInteractionsIntent(DrugIntent):
    intent_name: ClassVar[str] = DRUG_INTERACTIONS
    other_drug_name: str

@dataclass
class DrugWarningsIntent(DrugIntent):
    intent_name: ClassVar[str] = DRUG_WARNINGS

@dataclass
class DrugIndicationsAndUsage(DrugIntent):
    intent_name: ClassVar[str] = DRUG_INDICATIONS_AND_USAGE

@dataclass
class UnknownIntent(Intent):
    message: str | None


@dataclass
class IntentUndetermined(Intent):
    message: str | None

@dataclass
class IntentRequiresSlotElicitation(IntentUndetermined):
    intent_name: str
    slot_name: str

@dataclass
class IntentRequiresConfirmation(IntentUndetermined):
    intent_name: str
    slots: dict[str, str]

@dataclass
class IntentRecognitionInProgress(IntentUndetermined):
    pass

