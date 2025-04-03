"""
Chalice Translation Service Implementation

This service implements the TranslationService interface for Chalice without using AWS.
This is a fallback implementation when AWS Translate is not available.
"""

from typing import Tuple
from core.services.translation_service_interface import TranslationService
import logging
import re

logger = logging.getLogger(__name__)

class ChaliceTranslationService(TranslationService):
    """Simple implementation of translation service without AWS dependencies"""
    
    def __init__(self):
        # Setup language detection patterns 
        self.lang_patterns = {
            'ko': r'[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f\ua960-\ua97f\ud7b0-\ud7ff]+',  # Korean
            'ja': r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf\u3400-\u4dbf]+',  # Japanese
            'zh': r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]+',  # Chinese
            'es': r'[¿¡áéíóúüñ]+',  # Spanish
            'fr': r'[àâçéèêëîïôùûüÿæœ]+',  # French
            'de': r'[äöüß]+',  # German
        }
    
    def translate(self, text: str, source_lang: str = "auto", target_lang: str = "en") -> Tuple[str, str]:
        """
        Translate text between languages (simplified implementation)
        
        Args:
            text: Text to translate
            source_lang: Source language code (default: auto-detect)
            target_lang: Target language code (default: English)
            
        Returns:
            Tuple containing the translated text and the detected source language code
        """
        try:
            # Auto-detect language if needed
            detected_lang = source_lang
            if source_lang == "auto":
                detected_lang = self._detect_language(text)
            
            # If already in target language or we don't have translation capability
            if detected_lang == target_lang:
                return text, detected_lang
                
            # Simple message about lack of actual translation
            return f"[Translation from {detected_lang} to {target_lang} would happen here] {text}", detected_lang
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return text, "en"
            
    def _detect_language(self, text: str) -> str:
        """Simple language detection based on character patterns"""
        try:
            for lang, pattern in self.lang_patterns.items():
                if re.search(pattern, text):
                    return lang
            
            # Default to English if no patterns match
            return "en"
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return "en" 