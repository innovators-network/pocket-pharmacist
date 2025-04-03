"""
AWS Translate Service Implementation

Implements the TranslationService interface using AWS Translate.
"""

from typing import Tuple
import boto3
import logging
import os
from dotenv import load_dotenv
from core.services.translation_service_interface import TranslationService

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AWSTranslationService(TranslationService):
    """AWS Translate Service Implementation"""
    
    def __init__(self):
        # Get region from environment variables, with fallback to default
        region_name = os.getenv('TRANSLATE_REGION', os.getenv('AWS_REGION', 'us-east-1'))
        self.translate_client = boto3.client('translate', region_name=region_name)
    
    def translate(self, text: str, source_lang: str = "auto", target_lang: str = "en") -> Tuple[str, str]:
        """
        Translate text using AWS Translate
        
        Args:
            text: Text to translate
            source_lang: Source language code (default: auto-detect)
            target_lang: Target language code (default: English)
            
        Returns:
            Tuple containing the translated text and the detected source language code
        """
        try:
            # Use AWS Translate's auto-detect if source language is 'auto'
            aws_source_lang = 'auto' if source_lang == 'auto' else source_lang
            
            response = self.translate_client.translate_text(
                Text=text,
                SourceLanguageCode=aws_source_lang,
                TargetLanguageCode=target_lang
            )
            
            return response['TranslatedText'], response['SourceLanguageCode']
        
        except Exception as e:
            logger.error(f"AWS Translate error: {str(e)}")
            # Return original text if error occurs
            return text, source_lang 