import boto3
import logging
from chalicelib.translation_service import TranslationService

# Simple test script for the translation service

def test_translation():
    """Test the translation service."""
    service = TranslationService()
    
    # Test English to French
    english_text = "Hello, how are you feeling today?"
    french_translation = service.translate_text(english_text, source_lang='en', target_lang='fr')
    print(f"Original (EN): {english_text}")
    print(f"Translated (FR): {french_translation}")
    
    # Test French to English
    french_text = "Bonjour, comment vous sentez-vous aujourd'hui?"
    english_translation = service.translate_text(french_text, source_lang='fr', target_lang='en')
    print(f"Original (FR): {french_text}")
    print(f"Translated (EN): {english_translation}")
    
    # Test auto-detection
    spanish_text = "Hola, ¿cómo se siente hoy?"
    english_translation = service.translate_text(spanish_text, source_lang='auto', target_lang='en')
    print(f"Original (Auto-detect): {spanish_text}")
    print(f"Translated (EN): {english_translation}")

if __name__ == "__main__":
    test_translation()