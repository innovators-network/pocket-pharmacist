from typing import Dict, Any
import uuid
from ..orchestration.query_handler_interface import QueryHandler

class ChatbotInterface:
    """
    Pure business logic interface for the chatbot
    This class is not dependent on any web framework or external service.
    """
    def __init__(self):
        self.query_handler = QueryHandler()

    def handle_user_input(self, user_input: str, language: str = "auto") -> Dict[str, Any]:
        """
        Process user input and return appropriate response
        Args:
            user_input: User input in any supported language
            language: Source language code (default: auto-detect)
        Returns:
            Dictionary containing response data
        """
        # Generate a unique session ID for each conversation
        session_id = str(uuid.uuid4())
        
        return self.query_handler.process_query(
            query=user_input,
            session_id=session_id,
            source_lang=language
        )

    def format_response(self, response_data: Dict[str, Any]) -> str:
        """
        Format the response data into user-friendly message
        Args:
            response_data: Response data from services
        Returns:
            Formatted string response
        """
        if response_data.get("status") == "error":
            return response_data.get("response", "An error occurred")
            
        # If translated response exists, use it, otherwise use the original response
        return response_data.get("translated_response") or response_data.get("response", "") 