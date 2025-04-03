from chalice import Chalice, CORSConfig, Response
from corelib.interfaces.chatbot import Chatbot
import logging
import os
from typing import Dict, Any, override
from chalicelib.services.translation_service import AWSTranslationService
from chalicelib.services.intent_recognition_service import AWSIntentRecognitionService
from chalicelib.services.medical_info_service import AWSMedicalInfoService
from corelib.orchestration.query_handler import QueryHandler
from corelib.application import Application

class ChaliceApplication(Application):

    def __init__(self, query_handler: QueryHandler, chatbot: Chatbot):
        self.logger = logging.getLogger(__name__)

        # CORS configuration
        ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'https://your-frontend-domain.com')
        self.cors_config = CORSConfig(
            allow_origin=ALLOWED_ORIGINS,
            allow_headers=['Content-Type', 'X-Amz-Date', 'Authorization', 'X-Api-Key'],
            max_age=600
        )

        self.app = Chalice(app_name='pocket-pharmacist')
        self.query_handler = query_handler
        self.chatbot = chatbot


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
        def chat():
            try:
                request_body = self.app.current_request.json_body
                if not request_body:
                    raise APIError('Missing request body', status_code=400)

                if 'message' not in request_body:
                    raise APIError('Missing message in request', status_code=400)

                message = request_body['message']
                language = request_body.get('language', 'auto')

                # Validate message
                if not isinstance(message, str) or not message.strip():
                    raise APIError('Invalid message format', status_code=400)

                # Process the message
                response = self.chatbot.handle_user_input(message, language)

                return Response(
                    body=response,
                    status_code=200
                )

            except APIError as e:
                self.logger.error(f"API Error: {str(e)}", extra={'status_code': e.status_code, 'details': e.details})
                return Response(
                    body={
                        'error': e.message,
                        'details': e.details,
                        'status': 'error'
                    },
                    status_code=e.status_code
                )
            except Exception as e:
                self.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
                return Response(
                    body={
                        'error': 'Internal server error',
                        'status': 'error'
                    },
                    status_code=500
                )

class APIError(Exception):
    def __init__(self, message: str, status_code: int = 500, details: Dict[str, Any] | None = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)