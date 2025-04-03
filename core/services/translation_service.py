"""
Translation Service Interface

This service is responsible for translating text between different languages.
It is not dependent on any specific translation service implementation (e.g., AWS Translate).
"""

from typing import Tuple

class TranslationService:
    """Defines the interface for the translation service"""
    
    def translate(self, text: str, source_lang: str = "auto", target_lang: str = "en") -> Tuple[str, str]:
        """
        Translate text from one language to another
        
        Args:
            text: Text to translate
            source_lang: Source language code (default: auto-detect)    
            target_lang: Target language code (default: English)
            
        Returns:
            Tuple containing the translated text and the detected source language code
        """
        # This interface requires actual implementation
        # Basic implementation returns the original text without translation        
        return text, source_lang 