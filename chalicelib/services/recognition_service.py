import traceback
from typing import override, Any

import boto3
import logging
import json

from core.services.interfaces import IntentRecognitionService, IntentRecognitionResponse
from core.types.intents import (
    UnknownIntent, DrugIntent, Intent,
    DrugSideEffectsIntent,
    DrugDosageIntent,
    DrugInteractionsIntent,
    DrugWarningsIntent
)

logger = logging.getLogger(__name__)

class AWSIntentRecognitionService(IntentRecognitionService):

    def __init__(self, bot_id, bot_alias_id):
        self.lex_client = boto3.client('lexv2-runtime')
        self.bot_id = bot_id
        self.bot_alias_id = bot_alias_id

    @override
    def initialize(self):
        # No initialization needed for boto3 client
        pass

    @override
    def cleanup(self):
        # No cleanup needed for boto3 client
        pass

    @override
    def recognize_intent(self, text: str, session_id: str, session_state: Any | None) -> IntentRecognitionResponse:
        try:
            return self._recognize_intent(text, session_id, session_state)
        except Exception as e:
            logger.error(f"Error recognizing intent: {e}")
            traceback.print_exc()
            return IntentRecognitionResponse(
                intent = UnknownIntent(message="Error recognizing intent"),
                session_id = session_id,
                session_state = session_state
            )

    def _recognize_intent(self, text: str, session_id: str, session_state: Any | None) -> IntentRecognitionResponse:
        logger.info("Recognizing input text: %s", text)
        logger.info("Input Session state: %s", json.dumps(session_state, indent=2))
        response = self.lex_client.recognize_text(
            botId = self.bot_id,
            botAliasId = self.bot_alias_id,
            localeId = 'en_US',  # We'll use English for Lex after translation
            sessionId = session_id,
            sessionState = session_state or {},
            text = text
        )
        response_session_state = response.get('sessionState', None)
        interpretations = response.get('interpretations', None)
        if not interpretations or len(interpretations) == 0:
            logger.warning("No interpretations found in Lex response")
            return IntentRecognitionResponse(
                intent = UnknownIntent(message="Please be more specific with your request."),
                session_id = session_id,
                session_state = response_session_state
            )

        interpretation: dict[str, dict] = interpretations[0]
        intent: dict[str, Any] | None = interpretation.get('intent', None)
        intent_name: str | None = intent.get('name', None) if intent else None

        logger.info("Recognized Intent:%s", json.dumps(intent, indent=2))
        logger.info("Recognized Response Session state: %s", json.dumps(response_session_state, indent=2))

        if not intent or intent.get("name", None) is None:
            logger.warning("No intent found in Lex response")
            return IntentRecognitionResponse(
                intent = UnknownIntent(message="Please be more specific with your request."),
                session_id = session_id,
                session_state = session_state # Retain the original session state
            )

        recognized_intent: Intent | None = None

        if intent is not None and intent_name is not None:
            if intent_name == DrugSideEffectsIntent.intent_name:
                recognized_intent = self._recognize_side_effects_intent(session_id, intent, session_state)
            elif intent_name == DrugDosageIntent.intent_name:
                recognized_intent = self._recongize_dosage_intent(session_id, intent, session_state)
            elif intent_name == DrugInteractionsIntent.intent_name:
                recognized_intent = self._recognize_interactions_intent(session_id, intent, session_state)
            elif intent_name == DrugWarningsIntent.intent_name:
                recognized_intent = self._recongize_warnings_intent(session_id, intent, session_state)

        if recognized_intent is None:
            recognized_intent = UnknownIntent(message="Please be more specific with your request.")

        input_session_state_slots = self._get_field(session_state, ['intent', 'slots'], None)
        response_session_state_slots = self._get_field(response_session_state, ['intent', 'slots'], None)
        if response_session_state_slots and input_session_state_slots:
            if response_session_state_slots.get('DrugName', None) is None:
                response_session_state_slots['DrugName'] = input_session_state_slots.get('DrugName', None)

        logger.info("Response Session state: %s", json.dumps(response_session_state, indent=2))

        return IntentRecognitionResponse(
            intent = recognized_intent,
            session_id = session_id,
            session_state = response_session_state
        )

    def _get_field(self, data: Any, path: list[str], defalut: Any | None) -> Any | None:
        value: Any | None = data
        for field in path:
            # logger.info("Value type: %s, %s", type(value), value)
            # logger.info("Field: '%s'", field)
            if value is not None and isinstance(value, dict):
                value = value.get(field, None)
                # logger.info("Field: '%s': %s", field, value)
            else:
                return defalut
        return value

    def _get_drug_name_from_intent(self, intent: dict, slot_type: str = "DrugName") -> str | None:
        return self._get_field(intent, ['slots', slot_type, 'value', 'interpretedValue'], None)

    def _get_drug_name_from_session_state(self, session_state: dict | None, slot_type: str = "DrugName") -> str | None:
        session_intent_name = self._get_field(session_state, ['intent', 'name'], None)
        return self._get_field(session_state, ['intent', 'slots', slot_type, 'value', 'interpretedValue'], None)

    def _get_drug_name(self, intent: dict, session_state: dict | None, slot_type: str = "DrugName") -> str | None:
        drug_name = self._get_drug_name_from_intent(intent, slot_type)
        logger.info("Drug name obtained from intent: %s", drug_name)
        if drug_name is None:
            drug_name = self._get_drug_name_from_session_state(session_state, slot_type)
            logger.info("Drug name obtained from session state: %s", drug_name)

        return drug_name

    def _recognize_side_effects_intent(self, session_id: str, intent: dict, session_state: dict | None) -> Intent:
        logger.info("Drug side effects intent recognized")
        drug_name = self._get_drug_name(intent, session_state)
        logger.info("Drug name: %s", drug_name)
        return DrugSideEffectsIntent(drug_name=drug_name) if drug_name is not None \
            else UnknownIntent("Please provide a drug name.")

    def _recongize_dosage_intent(self, session_id: str, intent: dict, session_state: dict | None) -> Intent:
        logger.info("Drug dosage intent recognized")
        drug_name = self._get_drug_name(intent, session_state)
        logger.info("Drug name: %s", drug_name)
        return DrugDosageIntent(drug_name=drug_name) if drug_name is not None \
            else UnknownIntent("Please provide a drug name.")

    def _recognize_interactions_intent(self, session_id: str, intent: dict, session_state: dict | None) -> Intent:
        logger.info("Drug interactions intent recognized")
        drug_name = self._get_drug_name(intent, session_state)
        other_drug_name = self._get_drug_name(intent, session_state, "OtherDrug")
        logger.info("Drug name: %s", drug_name)
        logger.info("Other Drug name: %s", other_drug_name)
        return DrugInteractionsIntent(
            drug_name = drug_name,
            other_drug_name = other_drug_name
        ) if drug_name is not None and other_drug_name is not None\
            else UnknownIntent("Please provide two drug name.")

    def _recongize_warnings_intent(self, session_id: str, intent: dict, session_state: dict | None) -> Intent:
        logger.info("Drug warnings intent recognized")
        drug_name = self._get_drug_name(intent, session_state)
        logger.info("Drug name: %s", drug_name)
        return DrugWarningsIntent(drug_name=drug_name) if drug_name is not None \
            else UnknownIntent("Please provide a drug name.")
