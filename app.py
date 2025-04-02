import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from corelib.app import App
from corelib.orchestration.query_handler import QueryHandler
from corelib.interfaces.chatbot import Chatbot

#
# Manual Dependency Injection by injecting AWS specific implementations.
#

from chalicelib.chalice_app import ChaliceApp
from chalicelib.services.translation_service import AWSTranslationService
from chalicelib.services.intent_recognition_service import AWSIntentRecognitionService
from chalicelib.services.medical_info_service import AWSMedicalInfoService

query_handler = QueryHandler(
    translation_service = AWSTranslationService(),
    intent_service = AWSIntentRecognitionService(),
    medical_service = AWSMedicalInfoService()
)

chatbot = Chatbot(query_handler)

app: App = ChaliceApp(
    query_handler = query_handler,
    chatbot = chatbot
)

app.start() # Start the application


