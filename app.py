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
from chalicelib.services.recognition_service import AWSIntentRecognitionService
from fda.services.medical_service import OpenFDAMedicalInfoService

# Replace with your actual Lex bot ID and alias ID
lex_bot_id = "SKB6O0KIL2"
lex_bot_alias_id = "TSTALIASID"

query_handler = QueryHandler(
    translation_service = AWSTranslationService(),
    intent_recognition_service= AWSIntentRecognitionService(lex_bot_id, lex_bot_alias_id),
    medical_service = OpenFDAMedicalInfoService(config={"fda_api_url": "https://api.fda.gov"})
)

chatbot = Chatbot(query_handler)
application: Application = ChaliceApplication(chatbot = chatbot)

app = application.start() # Start the application and get the Chalice app object


