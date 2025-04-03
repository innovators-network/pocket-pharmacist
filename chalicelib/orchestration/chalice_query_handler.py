"""
Chalice Environment-Specific QueryHandler Adapter

Extends the QueryHandler from core to integrate with AWS services.
"""

from core.orchestration.query_handler_interface import QueryHandler
from ..services.aws_translation_service import AWSTranslationService
from ..services.chalice_intent_recognition import ChaliceIntentRecognitionService
from ..services.chalice_medical_info import ChalliceMedicalInfoService
import logging

logger = logging.getLogger(__name__)

class ChaliceQueryHandler(QueryHandler):
    """Implementation of QueryHandler using Chalice and AWS services"""
    
    def __init__(self):
        super().__init__()
        # Replace core services with AWS implementations
        self.translation_service = AWSTranslationService()
        self.intent_service = ChaliceIntentRecognitionService()
        self.medical_service = ChalliceMedicalInfoService()
        
    def initialize(self):
        """Initialize AWS service connections"""
        super().initialize()
        logger.info("Initializing AWS services for Chalice environment")
        
    def cleanup(self):
        """Clean up AWS service connections"""
        super().cleanup()
        logger.info("Cleaning up AWS service connections") 