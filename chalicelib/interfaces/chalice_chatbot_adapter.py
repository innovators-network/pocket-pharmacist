from typing import Dict, Any
from core.interfaces.chatbot_interface import ChatbotInterface as CoreChatbotInterface
from ..orchestration.chalice_query_handler import ChaliceQueryHandler

class ChatbotInterface:
    """
    Chalice API Adapter Layer
    
    This class serves as an adapter between the Chalice framework and pure business logic.
    It performs API-specific processing and delegates core business logic to the core package.
    """
    def __init__(self):
        # Use the Chalice-specific QueryHandler directly instead of the core interface
        self.query_handler = ChaliceQueryHandler()

    def handle_user_input(self, user_input: str, language: str = "auto") -> Dict[str, Any]:
        """
        Process user input coming from Chalice API
        Args:
            user_input: User text input
            language: Source language code (default: auto-detect)
        Returns:
            Dictionary suitable for API response
        """
        # API-specific preprocessing logic
        session_id = "chalice-session-" + str(hash(user_input))[:8]
        
        # Delegate to core business logic
        return self.query_handler.process_query(
            query=user_input,
            session_id=session_id,
            source_lang=language
        )
        
    def format_response(self, response_data: Dict[str, Any]) -> str:
        """
        Format the API response data
        Args:
            response_data: Response data from services
        Returns:
            String response suitable for API
        """
        # API-specific post-processing logic
        if response_data.get("status") == "error":
            return response_data.get("response", "An error occurred")
            
        # If translated response exists, use it, otherwise use the original response
        return response_data.get("translated_response") or response_data.get("response", "") 