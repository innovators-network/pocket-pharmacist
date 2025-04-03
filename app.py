import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from core.application import Application
from core.orchestration.query_handler import QueryHandler
from core.interfaces.chatbot import Chatbot

#
# Manual Dependency Injection by injecting AWS specific implementations.
#

from chalicelib.chalice_application import ChaliceApplication
from chalicelib.services.translation_service import AWSTranslationService
from chalicelib.services.intent_recognition_service import AWSIntentRecognitionService
from chalicelib.services.medical_info_service import AWSMedicalInfoService

query_handler = QueryHandler(
    translation_service = AWSTranslationService(),
    intent_service = AWSIntentRecognitionService(),
    medical_service = AWSMedicalInfoService()
)

chatbot = Chatbot(query_handler)

application: Application = ChaliceApplication(
    query_handler = query_handler,
    chatbot = chatbot
)

app = application.start() # Start the application and get the Chalice app object


