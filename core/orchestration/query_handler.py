import logging

from typing import Dict, Any, Optional, override
from dataclasses import dataclass, replace
from core.services.medical_info_service import MedicalInfoError, MedicalInfo, MedicalInfoService
from core.services.translation_service import TranslationService
from core.services.intent_recognition_service import (
    IntentRecognitionService,
    IntentRecognitionResponse,

)
from datetime import datetime, timedelta

from core.types.intents import UnknownIntent, Intent, DrugIntent, DrugInteractionsIntent, DrugSideEffectsIntent, \
    IntentUndetermined

logger = logging.getLogger(__name__)

@dataclass
class QueryRequest:
    text: str
    session_id: str
    session_state: Any | None
    language: str | None

@dataclass
class QueryResponse:
    text: str
    session_id: str
    session_state: Any | None
    language: str | None


ENGLISH = "en"

class QueryHandler:

    def __init__(
        self,
        translation_service: TranslationService,
        intent_recognition_service = IntentRecognitionService,
        medical_service = MedicalInfoService
    ):
        self.translation_service = translation_service
        self.intent_recognition_service = intent_recognition_service
        self.medical_service = medical_service
        self.session_timeout = timedelta(hours = 24)  # Session timeout after 24 hours

    def initialize(self):
        self.translation_service.initialize()
        self.intent_recognition_service.initialize()
        self.medical_service.initialize()

    def cleanup(self):
        self.medical_service.cleanup()
        self.intent_recognition_service.cleanup()
        self.translation_service.cleanup()

    def process_query(self, query: QueryRequest) -> QueryResponse:
        try:
            return self._process_query(query)
        except Exception as e:
            return QueryResponse(
                text = str(e),
                session_id = query.session_id,
                session_state = query.session_state,
                language = query.language
            )

    def _process_query(self, query: QueryRequest) -> QueryResponse:
        logger.info(f"Processing query for session {query.session_id}: {query.text}")

        session_state = query.session_state
        source_lang = query.language
        translated_text_in_english, detected_source_lang, _ = self.translation_service.translate_text(query.text, source_lang, ENGLISH)
        if not translated_text_in_english:
            return QueryResponse(
                text = f"Translation failed, language: {source_lang}",
                session_id = query.session_id,
                session_state = session_state,
                language = ENGLISH
            )

        if source_lang is None and detected_source_lang is None:
            return QueryResponse(
                text = f"Language detection failed, language: {source_lang}",
                session_id = query.session_id,
                session_state = session_state
            )
        elif detected_source_lang != source_lang:
            logger.warning(f"Detected source language: {detected_source_lang}, expected: {source_lang}")
        else:
            logger.info(f"Detected source language: {detected_source_lang}")

        intent_recognition_response: IntentRecognitionResponse = self.intent_recognition_service.recognize_intent(translated_text_in_english, query.session_id, session_state)
        intent = intent_recognition_response.intent
        session_state = intent_recognition_response.session_state

        if isinstance(intent, (UnknownIntent, IntentUndetermined)):
            message = intent.message or "Failed to recognize intent"
            translated_message, _, _ = self.translation_service.translate_text(message, ENGLISH, detected_source_lang)
            return QueryResponse(
                text = translated_message,
                session_id = query.session_id,
                session_state = session_state,
                language = detected_source_lang
            )

        assert isinstance(intent, DrugIntent)
        medical_info: MedicalInfo = self.medical_service.get_medical_info(intent)
        medical_info_message = medical_info.message
        logger.info("Medical info message in English: %s", medical_info_message)
        if isinstance(medical_info, MedicalInfoError):
            translated_error_message, _, _ = self.translation_service.translate_text(medical_info_message, ENGLISH, detected_source_lang)
            return QueryResponse(
                text = translated_error_message,
                session_id = query.session_id,
                session_state = session_state,
                language = detected_source_lang
            )

        translated_medical_info_message, _, _ = self.translation_service.translate_text(medical_info_message, ENGLISH, detected_source_lang)
        return QueryResponse(
            text = translated_medical_info_message,
            session_id = query.session_id,
            session_state = session_state,
            language = detected_source_lang
        )
