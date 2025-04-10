import json

from chalice import Chalice, CORSConfig, Response
import logging
from typing import Dict, Any, override
from dataclasses import asdict

from core.interfaces.chatbot import Chatbot, ChatMessage
from core.application import Application

class ChaliceApplication(Application):

    def __init__(self, chatbot: Chatbot, allowed_origins: str | None = None):
        self.logger = logging.getLogger(__name__)
        if allowed_origins:
            self.cors_config = CORSConfig(
                allow_origin=allowed_origins,
                allow_headers=['Content-Type', 'X-Amz-Date', 'Authorization', 'X-Api-Key'],
                max_age=600
            )
        else:
            self.cors_config = CORSConfig()

        self.app: Chalice = Chalice(app_name='pocket-pharmacist')
        self.chatbot: Chatbot = chatbot


    @override
    def start(self) -> Any:
        self._setup_routes()
        return self.app

    def _setup_routes(self):

        @self.app.route('/', cors=self.cors_config)
        def index():
            return Response(
                body={'message': 'Pocket Pharmacist API'},
                status_code=200
            )

        @self.app.route('/api/chat', methods=['POST'], cors=self.cors_config)
        def chat() -> Response:
            response: Response = self._chat_with_error_handling()
            print("Response JSON:", response.body)
            return response

    def _chat_with_error_handling(self) -> Response:
        try:
            return self._chat()
        except APIError as e:
            self.logger.error(f"API Error: {str(e)}", extra={'status_code': e.status_code, 'details': e.details})
            return Response(
                body = {
                    'error': e.message,
                    'details': e.details,
                    'status': 'error'
                },
                status_code=e.status_code
            )
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response(
                body = {
                    'error': 'Internal server error',
                    'status': 'error'
                },
                status_code=500
            )

    def _chat(self) -> Response:
        current_request = self.app.current_request
        if not current_request:
            raise APIError('Invalid request', status_code=400)

        request_body: Any = current_request.json_body if current_request else None
        print("Request Body:", json.dumps(request_body, indent=2))
        session_id = request_body['sessionId']
        timestamp = request_body['timestamp']
        text = request_body['text']
        language = request_body.get('language', 'en_US')
        context = request_body.get('context', None)
        if not isinstance(text, str) or not text.strip():
            raise APIError('Invalid message format', status_code=400)

        chat_message = ChatMessage(
            sessionId=session_id,
            timestamp=timestamp,
            text=text,
            language=language,
            context=context
        )
        response: ChatMessage = self.chatbot.handle_chat_message(chat_message)
        response_dict = asdict(response)
        return Response(
            body=response_dict,
            status_code=200
        )

class APIError(Exception):
    def __init__(self, message: str, status_code: int = 500, details: Dict[str, Any] | None = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)