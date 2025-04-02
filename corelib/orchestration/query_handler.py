"""
Orchestration Layer Implementation
Team: Member 4 (Orchestration Layer Team)
Responsibilities:
- Manage the overall flow of the application
- Handle service integration
- Manage session data
- Error handling and logging

Implementation Notes:
1. Current Implementation:
   - Basic service orchestration
   - Multi-language support through AWS Translate
   - Session management
   - Error handling
   - Translation flow

2. TODO:
   - Enhance data retrieval flow:
     * Integrate with S3 for stored data
     * Integrate with DynamoDB for metadata
   - Add caching layer for frequent queries
   - Implement rate limiting
   - Add monitoring and metrics
"""

from typing import Dict, Any, Optional
from corelib.services.interfaces import TranslationService
from corelib.services.interfaces import IntentRecognitionService
from corelib.services.interfaces import MedicalInfoService
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class QueryHandler:
    def __init__(
        self,
        translation_service: TranslationService,
        intent_service = IntentRecognitionService,
        medical_service = MedicalInfoService
    ):
        self.translation_service = translation_service
        self.intent_service = intent_service
        self.medical_service = medical_service
        self.session_data: Dict[str, Any] = {}
        self.session_timeout = timedelta(hours=24)  # Session timeout after 24 hours

    def initialize(self):
        """Initialize all services"""
        self.medical_service.initialize()
        # Other services will be initialized by their respective teams

    def cleanup(self):
        """Cleanup all services"""
        self.medical_service.cleanup()
        # Other services will be cleaned up by their respective teams

    def process_query(
        self, 
        query: str, 
        session_id: str,
        source_lang: str = "auto", 
        target_lang: str = "en"
    ) -> Dict[str, Any]:
        """
        Main orchestration method to process user queries
        Args:
            query: User's input text in any supported AWS Translate language
            session_id: Unique session identifier
            source_lang: Source language code (default: auto-detect)
            target_lang: Target language for response
        Returns:
            Processed response with medical information
        """
        try:
            logger.info(f"Processing query for session {session_id}: {query}")
            
            # Clean up expired sessions
            self._cleanup_expired_sessions()
            
            # Step 1: Translate query to English for processing
            translated_query = self._handle_translation(query, source_lang, "en")
            if not translated_query:
                return self._create_error_response("Translation failed", source_lang)

            # Step 2: Get intent from Lex (English input)
            intent_data = self.intent_service.recognize_intent(translated_query)
            if not intent_data.get('intent'):
                return self._create_error_response("Could not understand the query", source_lang)

            # Step 3: Get information based on intent
            medical_response = self._get_medical_info(intent_data, session_id)
            if medical_response.get("status") == "error":
                return self._create_error_response(medical_response.get("message", "Unknown error"), source_lang)

            # Step 4: Translate response to target language
            final_response = self._prepare_final_response(
                medical_response,
                source_lang,
                target_lang
            )

            # Step 5: Update session data
            self._update_session_data(session_id, {
                "last_query": query,
                "last_intent": intent_data.get('intent'),
                "timestamp": datetime.utcnow().isoformat(),
                "query_count": self.session_data.get(session_id, {}).get("query_count", 0) + 1
            })

            return final_response

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            return self._create_error_response("An unexpected error occurred", source_lang)

    def _handle_translation(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str
    ) -> Optional[str]:
        """
        Handle translation of text between languages
        """
        try:
            if source_lang == target_lang:
                return text
                
            translated_text = self.translation_service.translate_text(text, source_lang, target_lang)
            return translated_text
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return None

    def _get_medical_info(
        self, 
        intent_data: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """
        Get medical information based on intent
        """
        try:
            return self.medical_service.get_medical_info(intent_data)
        except Exception as e:
            logger.error(f"Error getting medical info: {str(e)}")
            return self._create_error_response("Failed to retrieve medical information", "en")

    def _prepare_final_response(
        self,
        medical_response: Dict[str, Any],
        source_lang: str,
        target_lang: str
    ) -> Dict[str, Any]:
        """
        Prepare the final response with translations
        """
        try:
            if source_lang != target_lang:
                translated_response = self._handle_translation(
                    medical_response.get("response", ""),
                    "en",
                    target_lang
                )
                if translated_response:
                    medical_response["translated_response"] = translated_response

            return medical_response
        except Exception as e:
            logger.error(f"Error preparing response: {str(e)}")
            return medical_response

    def _update_session_data(self, session_id: str, data: Dict[str, Any]) -> None:
        """
        Update session data with new information
        """
        if session_id not in self.session_data:
            self.session_data[session_id] = {}
        self.session_data[session_id].update(data)

    def _cleanup_expired_sessions(self) -> None:
        """
        Remove expired sessions from session data
        """
        current_time = datetime.utcnow()
        expired_sessions = [
            session_id for session_id, data in self.session_data.items()
            if current_time - datetime.fromisoformat(data["timestamp"]) > self.session_timeout
        ]
        for session_id in expired_sessions:
            del self.session_data[session_id]

    def _create_error_response(self, error_message: str, language: str) -> Dict[str, Any]:
        """
        Create standardized error response
        """
        return {
            "status": "error",
            "message": error_message,
            "response": error_message,
            "language": language
        } 