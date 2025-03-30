import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add parent directory to path to import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from chalicelib.translation_service import TranslationService

class TestTranslationService(unittest.TestCase):
    @patch('boto3.client')
    def test_translate_text(self, mock_boto_client):
        # Create a mock for the translate client
        mock_translate = MagicMock()
        mock_boto_client.return_value = mock_translate
        
        # Set up the mock to return a specific response
        mock_translate.translate_text.return_value = {
            'TranslatedText': 'Hello, how are you feeling today?',
            'SourceLanguageCode': 'fr',
            'TargetLanguageCode': 'en'
        }
        
        # Initialize the service
        service = TranslationService()
        
        # Test the translation
        result = service.translate_text('Bonjour, comment vous sentez-vous aujourd\'hui?', 'fr', 'en')
        
        # Assert the method was called with the correct parameters
        mock_translate.translate_text.assert_called_with(
            Text='Bonjour, comment vous sentez-vous aujourd\'hui?',
            SourceLanguageCode='fr',
            TargetLanguageCode='en'
        )
        
        # Assert the result is what we expect
        self.assertEqual(result, 'Hello, how are you feeling today?')
    
    @patch('boto3.client')
    def test_empty_text(self, mock_boto_client):
        # Create a mock for the translate client
        mock_translate = MagicMock()
        mock_boto_client.return_value = mock_translate
        
        # Initialize the service
        service = TranslationService()
        
        # Test with empty text
        result = service.translate_text('')
        
        # The method should return empty string without calling the API
        mock_translate.translate_text.assert_not_called()
        self.assertEqual(result, '')
    
    @patch('boto3.client')
    def test_translation_error(self, mock_boto_client):
        # Create a mock for the translate client
        mock_translate = MagicMock()
        mock_boto_client.return_value = mock_translate
        
        # Set up the mock to raise an exception
        mock_translate.translate_text.side_effect = Exception("Translation failed")
        
        # Initialize the service
        service = TranslationService()
        
        # Test the translation with an error
        result = service.translate_text('Test text')
        
        # Assert the method returns None on error
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()