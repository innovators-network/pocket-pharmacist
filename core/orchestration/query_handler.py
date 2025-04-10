
from typing import Dict, Any, Optional, override
from dataclasses import dataclass
from core.services.interfaces import TranslationService, MedicalInfoError, MedicalInfo
from core.services.interfaces import IntentRecognitionService
from core.services.interfaces import MedicalInfoService
import logging
from datetime import datetime, timedelta

from core.types.intents import UnknownIntent

logger = logging.getLogger(__name__)

@dataclass
class QueryRequest:
    text: str
    session_id: str
    session_state: Any | None = None
    language: str | None = None

@dataclass
class QuerySuccess:
    text: str
    session_id: str
    session_state: Any | None = None
    language: str | None = None

@dataclass
class QueryFailure:
    error: str
    session_id: str

type QueryResponse = QuerySuccess | QueryFailure

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
        self.session_data: Dict[str, Any] = {}
        self.session_timeout = timedelta(hours=24)  # Session timeout after 24 hours

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
            return QueryFailure(
                error=str(e),
                session_id=query.session_id
            )

    def _process_query(self, query: QueryRequest) -> QueryResponse:
        logger.info(f"Processing query for session {query.session_id}: {query.text}")

        source_lang = query.language or "en_US"
        target_lang = "en_US"  # Default target language

        translated_text = self.translation_service.translate_text(query.text, source_lang, target_lang)
        if not translated_text:
            return QueryFailure(
                error = "Translation failed, language: " + source_lang,
                session_id = query.session_id
            )

        intent_response = self.intent_recognition_service.recognize_intent(translated_text, query.session_id, query.session_state)
        intent = intent_response.intent

        if isinstance(intent, UnknownIntent):
            error_text = "I'm sorry, I couldn't understand your request. Could you please rephrase it?"
            translated_error_text = self.translation_service.translate_text(error_text, target_lang, source_lang)
            return QueryFailure(
                error = translated_error_text,
                session_id = query.session_id
            )

        medical_info_response = self.medical_service.get_medical_info(intent)

        response: QueryResponse | None = None

        if isinstance(medical_info_response, MedicalInfo):
            medical_info = medical_info_response
            translated_medical_info_text = self.translation_service.translate_text(medical_info.message, target_lang, source_lang)
            response = QuerySuccess(
                text = medical_info.message,
                session_id = query.session_id,
                session_state = intent_response.session_state,
                language = target_lang
            )
        elif isinstance(medical_info_response, MedicalInfoError):
            error_text = medical_info_response.error
            translated_error_text = self.translation_service.translate_text(error_text, target_lang, source_lang)
            return QueryFailure(
                error = translated_error_text,
                session_id = query.session_id
            )
        else:
            logger.error("Unexpected response from medical service")
            return QueryFailure(
                error = "An unexpected error occurred while processing your request.",
                session_id = query.session_id
            )

        return response
