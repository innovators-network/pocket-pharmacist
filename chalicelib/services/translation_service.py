import boto3
import logging

from typing_extensions import override

from core.services.interfaces import TranslationService

logger = logging.getLogger(__name__)

class AWSTranslationService(TranslationService):

    def __init__(self):
        """Initialize the AWS Translate client."""
        self.translate_client = boto3.client('translate')

    @override
    def translate_text(self, text, source_lang='auto', target_lang='en') -> str | None:
        """
        Translate text from source language to target language.
        
        Args:
            text (str): Text to translate
            source_lang (str): Source language code (default: auto-detect)
            target_lang (str): Target language code (default: English)
            
        Returns:
            str: Translated text
        """
        try:
            if not text:
                return ""
                
            response = self.translate_client.translate_text(
                Text=text,
                SourceLanguageCode=source_lang,
                TargetLanguageCode=target_lang
            )
            
            return response['TranslatedText']
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return None