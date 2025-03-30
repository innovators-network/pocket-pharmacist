import boto3
import logging
import json

logger = logging.getLogger(__name__)

class IntentRecognitionService:
    def __init__(self, bot_id, bot_alias_id):
        """
        Initialize the AWS Lex client.
        
        Args:
            bot_id (str): Lex bot ID
            bot_alias_id (str): Lex bot alias ID
        """
        self.lex_client = boto3.client('lexv2-runtime')
        self.bot_id = bot_id
        self.bot_alias_id = bot_alias_id
        
    def recognize_intent(self, text, session_id):
        """
        Recognize user intent using AWS Lex.
        
        Args:
            text (str): User input text
            session_id (str): Unique session identifier
            
        Returns:
            dict: Intent recognition result
        """
        try:
            response = self.lex_client.recognize_text(
                botId=self.bot_id,
                botAliasId=self.bot_alias_id,
                localeId='en_US',  # We'll use English for Lex after translation
                sessionId=session_id,
                text=text
            )
            
            return {
                'intent_name': response.get('interpretations', [{}])[0].get('intent', {}).get('name'),
                'slots': response.get('interpretations', [{}])[0].get('intent', {}).get('slots', {}),
                'session_state': response.get('sessionState', {}),
                'messages': response.get('messages', [])
            }
        except Exception as e:
            logger.error(f"Intent recognition error: {str(e)}")
            return None