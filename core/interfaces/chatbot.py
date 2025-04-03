from typing import Dict, Any
import uuid
from core.orchestration.query_handler import QueryHandler

class Chatbot:

    def __init__(self, query_handler: QueryHandler):
        self.query_handler = query_handler

    def handle_user_input(self, user_input: str, language: str = "auto") -> Dict[str, Any]:
        """
        Handle user input and return appropriate response
        Args:
            user_input: The text input from user in any supported language
            language: Source language code (default: auto-detect)
        Returns:
            Dict containing response data
        """
        # Generate a unique session ID for each conversation
        # In a production environment, this should be managed by the web framework
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
            response_data: The response data from services
        Returns:
            Formatted string response
        """
        if response_data.get("status") == "error":
            return response_data.get("response", "An error occurred")
            
        # Use translated response if available, otherwise use original response
        return response_data.get("translated_response") or response_data.get("response", "") 