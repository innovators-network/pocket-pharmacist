import uuid
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from core.orchestration.query_handler import QueryHandler, QueryRequest, QuerySuccess, QueryFailure


@dataclass
class ChatMessage:
    sessionId: str
    timestamp: str
    text: str
    language: str | None = None
    context: Any | None = None

    @property
    def session_id(self) -> str:
        return self.sessionId

    @session_id.setter
    def session_id(self, session_id: str) -> None:
        self.sessionId = session_id


class Chatbot:

    def __init__(self, query_handler: QueryHandler):
        self.query_handler = query_handler

    def handle_chat_message(self, chat_message: ChatMessage) -> ChatMessage:
        session_id = chat_message.session_id

        query_request = QueryRequest(
            text = chat_message.text,
            session_id = session_id,
            session_state = chat_message.context,
            language = chat_message.language
        )
        
        query_response = self.query_handler.process_query(query_request)
        chat_response: ChatMessage
        if isinstance(query_response, QuerySuccess):
            chat_response = ChatMessage(
                sessionId = session_id,
                timestamp = chat_message.timestamp,
                text = query_response.text,
                language = chat_message.language,
                context = query_response.session_state
            )
        elif isinstance(query_response, QueryFailure):
            chat_response = ChatMessage(
                sessionId = session_id,
                timestamp = datetime.now().isoformat(),
                text = query_response.error,
                language = chat_message.language,
                context = query_request.session_state
            )
        else:
            raise ValueError("Invalid query response type")
        return chat_response
