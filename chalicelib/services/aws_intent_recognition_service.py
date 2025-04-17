import traceback
from typing import override, Any, TypeVar

import boto3
import logging
import json

from core.services.intent_recognition_service import (
    IntentRecognitionService,
    IntentRecognitionResponse,
)

from core.types.intents import (
    Intent,
    DrugIntent,
    DrugSideEffectsIntent,
    DrugDosageIntent,
    DrugInteractionsIntent,
    DrugWarningsIntent,
    DrugIndicationsAndUsage,
    UnknownIntent,
    IntentRequiresConfirmation,
    IntentRequiresSlotElicitation,
    IntentRecognitionInProgress,
)

logger = logging.getLogger(__name__)

T = TypeVar('T')

def get(obj: Any | None, path: list[str | int], default: T) -> T:
    value = obj
    for key in path:
        if isinstance(key, str) and isinstance(value, dict):
            value = value.get(key)
        elif isinstance(key, int) and isinstance(value, list) and (0 <= key < len(value) or (key < 0 and abs(key) <= len(value))):
            value = value[key]
        else:
            break
    return value if value is not None else default

class AWSIntentRecognitionService(IntentRecognitionService):

    def __init__(self, bot_id, bot_alias_id):
        self.lex_client = boto3.client('lexv2-runtime')
        self.bot_id = bot_id
        self.bot_alias_id = bot_alias_id
        self.locale_id = 'en_US'

    @override
    def initialize(self):
        pass

    @override
    def cleanup(self):
        pass

    @override
    def recognize_intent(self, text: str, session_id: str, session_state: Any | None) -> IntentRecognitionResponse:
        if session_state:
            assert isinstance(session_state, dict)

        response = self._recognize_intent(
            text=text,
            session_id=session_id,
            session_state=session_state or {},
            depth=0
        )

        return response

    def _recognize_intent(self, text: str, session_id: str, session_state: dict[str, Any], depth: int) -> IntentRecognitionResponse:
        if depth > 3:
            raise RuntimeError("Maximum recursion depth exceeded")

        print()
        print("Recognizing intent for text:", text)
        print("Session ID:", session_id)
        print("Session state:", json.dumps(session_state, indent=2))
        print("Depth:", depth)
        session_intent = get(session_state, ["intent"], None)
        session_intent_slots = get(session_intent, ["slots"], None)
        if session_intent and session_intent_slots:
            # Clean up slots with None values
            session_intent["slots"] = {key: value for key, value in session_intent_slots.items() if value is not None}
        response = self.lex_client.recognize_text(
            botId=self.bot_id,
            botAliasId=self.bot_alias_id,
            localeId=self.locale_id,
            sessionId=session_id,
            text=text,
            sessionState=session_state
        )
        print("Response (Lex):", json.dumps(response, indent=2))

        session_state = get(response, ["sessionState"], session_state)
        session_attributes: dict[str, Any] = get(response, ["sessionState", "sessionAttributes"], {})
        intent_name = get(response, ["sessionState", "intent", "name"], None)
        intent_state = get(response, ["sessionState", "intent", "state"], None)
        dialog_type: str | None = get(response, ["sessionState", "dialogAction", "type"], None)
        interpretations = get(response, ["interpretations"], None)
        message = get(response, ["messages", 0, "content"], None)

        print("Response Intent state: ", intent_state)

        if intent_state == 'Failed' or not interpretations or len(interpretations) == 0:
            print("Failed to recognize intent for text:", text)
            return IntentRecognitionResponse(
                intent=UnknownIntent(message=message),
                session_state=session_state,
            )

        if intent_state in ["ReadyForFulfillment", "Fulfilled"]:
            print("Successfully fulfilled intent for text:", text)
            drug_name = get(response, ["sessionState", "intent", "slots", "DrugName", "value", "interpretedValue"], None)
            other_drug_name = get(response, ["sessionState", "intent", "slots", "OtherDrug", "value", "interpretedValue"], None)
            print("Drug name:", drug_name)
            print("Other drug name:", other_drug_name)
            if drug_name is not None:
                session_attributes["DrugName"] = drug_name
                print("Session attributes updated with DrugName:", session_attributes["DrugName"])
            if other_drug_name is not None:
                session_attributes["OtherDrug"] = other_drug_name
                print("Session attributes updated with OtherDrug:", session_attributes["OtherDrug"])
            intent: Intent
            if intent_name == DrugSideEffectsIntent.intent_name and drug_name:
                intent = DrugSideEffectsIntent(drug_name=drug_name)
            elif intent_name == DrugDosageIntent.intent_name and drug_name:
                intent = DrugDosageIntent(drug_name=drug_name)
            elif intent_name == DrugInteractionsIntent.intent_name and drug_name and other_drug_name:
                intent = DrugInteractionsIntent(drug_name=drug_name, other_drug_name=other_drug_name)
            elif intent_name == DrugWarningsIntent.intent_name and drug_name:
                intent = DrugWarningsIntent(drug_name=drug_name)
            elif intent_name == DrugIndicationsAndUsage.intent_name and drug_name:
                intent = DrugIndicationsAndUsage(drug_name=drug_name)
            else:
                intent = UnknownIntent(message=message)

            session_state["sessionAttributes"] = session_attributes
            print("Session state updated with session attributes:", json.dumps(session_state, indent=2))
            return IntentRecognitionResponse(
                intent=intent,
                session_state=session_state
            )

        if intent_state in ["InProgress", "FulfillmentInProgress"]:
            if dialog_type == "ElicitSlot":
                slot_to_elicit = get(response, ["sessionState", "dialogAction", "slotToElicit"], None)
                slot_value = get(session_attributes, [slot_to_elicit], None)
                print("Expecting slot value for intent:", intent_name, "and slot:", slot_to_elicit)
                print("Slot value obtained from session_attributes:", slot_value)
                if slot_value:
                    # If the slot value is already set in session attributes, use it to
                    # elicit the slot again recursively:
                    print("Recursively recognizing intent with slot value:", slot_value)
                    return self._recognize_intent(
                        text=slot_value,
                        session_id=session_id,
                        session_state=session_state,
                        depth=depth + 1
                    )

                if intent_name and slot_to_elicit:
                    return IntentRecognitionResponse(
                        intent=IntentRequiresSlotElicitation(
                            intent_name=intent_name,
                            slot_name=slot_to_elicit,
                            message=message
                        ),
                        session_state=session_state
                    )

            if dialog_type == 'ConfirmIntent':
                print("Confirming intent for text:", text)
                intent_slots = get(response, ["sessionState", "intent", "slots"], None)
                if intent_name and intent_slots:
                    return IntentRecognitionResponse(
                        intent=IntentRequiresConfirmation(
                            intent_name=intent_name,
                            slots=intent_slots,
                            message=message
                        ),
                        session_state=session_state
                    )

            print("Assuming intent is still in progress for text:", text)
            return IntentRecognitionResponse(
                intent = IntentRecognitionInProgress(message=message,),
                session_state=session_state,
            )

        print("Unknown intent state:", intent_state, "for text:", text)
        return IntentRecognitionResponse(
            intent=UnknownIntent(message=message),
            session_state=session_state,
        )
