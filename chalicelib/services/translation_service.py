import boto3
import logging

from typing_extensions import override

from core.services.interfaces import TranslationService

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
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        try:
            return self._translate_text(text, source_lang, target_lang)
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            return text

    def _translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        if source_lang == target_lang or len(text.strip()) == 0:
            return text

        response = self.translate_client.translate_text(
            Text=text,
            SourceLanguageCode=source_lang,
            TargetLanguageCode=target_lang
        )
        return response['TranslatedText']
