import boto3
import logging

from charset_normalizer import detect
from typing_extensions import override

from core.services.translation_service import TranslationService

logger = logging.getLogger(__name__)

class AWSTranslationService(TranslationService):

    def __init__(self):
        self.translate_client = boto3.client('translate')

    @override
    def initialize(self):
        # No initialization needed for boto3 client
        pass

    @override
    def cleanup(self):
        # No cleanup needed for boto3 client
        pass

    @override
    def translate_text(self, text: str, source_lang: str | None, target_lang: str) -> tuple[str, str, str]:
        try:
            return self._translate_text(text, source_lang, target_lang)
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            raise e

    def _translate_text(self, text: str, source_lang: str | None, target_lang: str) -> tuple[str, str, str]:


        response = self.translate_client.translate_text(
            Text=text,
            SourceLanguageCode=source_lang or 'auto',
            TargetLanguageCode=target_lang
        )
        translated_text = response['TranslatedText']
        detected_source_lang = response['SourceLanguageCode']
        detected_target_lang = response['TargetLanguageCode']
        return translated_text, detected_source_lang, detected_target_lang
