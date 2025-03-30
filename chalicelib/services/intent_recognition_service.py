"""
Intent Recognition Service Implementation
Team: Member 1 (Lex + Polly Team)
Responsibilities:
- Implement intent recognition using AWS Lex
- Handle text-to-speech conversion
- Manage conversation flow

Implementation Notes:
1. Current Implementation:
   - Basic service structure
   - AWS Lex integration
   - Error handling and logging

2. TODO:
   - Add Polly integration for speech synthesis
   - Design conversation flows
   - Add support for medical terminology
   - Implement context awareness
"""

from typing import Dict, Any
import boto3
from botocore.config import Config
import logging
import os

logger = logging.getLogger(__name__)

class IntentRecognitionService:
    def __init__(self):
        self.client = boto3.client(
            'lexv2-runtime',
            config=Config(
                retries = dict(
                    max_attempts = 3
                )
            )
        )
        # Get bot configuration from environment variables
        self.bot_id = os.getenv('LEX_BOT_ID', 'YOUR_BOT_ID')
        self.bot_alias_id = os.getenv('LEX_BOT_ALIAS_ID', 'YOUR_BOT_ALIAS_ID')

        if self.bot_id == 'YOUR_BOT_ID' or self.bot_alias_id == 'YOUR_BOT_ALIAS_ID':
            logger.warning("Lex bot configuration not set. Please set LEX_BOT_ID and LEX_BOT_ALIAS_ID environment variables.")

    def recognize_intent(self, text: str) -> Dict[str, Any]:
        """
        Recognize intent using AWS Lex
        Args:
            text: User's input text
        Returns:
            Dictionary containing intent and slots information
        """
        try:
            if not text:
                logger.warning("Empty text provided for intent recognition")
                return {'intent': None, 'slots': {}}

            logger.info(f"Recognizing intent for text: {text[:50]}...")
            response = self.client.recognize_text(
                botId=self.bot_id,
                botAliasId=self.bot_alias_id,
                localeId='en_US',
                sessionId='test-session',  # Should be dynamic in production
                text=text
            )
            
            intent_data = {
                'intent': response.get('interpretations', [{}])[0].get('intent', {}),
                'slots': response.get('interpretations', [{}])[0].get('slots', {})
            }

            if intent_data['intent']:
                logger.info(f"Recognized intent: {intent_data['intent'].get('name', 'unknown')}")
            else:
                logger.warning("No intent recognized")

            return intent_data

        except Exception as e:
            logger.error(f"Intent recognition error: {str(e)}", exc_info=True)
            return {'intent': None, 'slots': {}} 