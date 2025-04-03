"""
Chalice Medical Information Service Implementation

This service implements the MedicalInfoService interface using AWS services and OpenFDA API.
"""

from typing import Dict, Any
from core.services.medical_info_interface import MedicalInfoService
import logging
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class ChalliceMedicalInfoService(MedicalInfoService):
    """AWS-based implementation of medical information service"""
    
    def __init__(self):
        self.openfda_api_key = os.getenv('OPENFDA_API_KEY', '')
        self.api_base_url = "https://api.fda.gov/drug"
        self.drug_database = {}  # In-memory cache, would use DynamoDB in production
        
    def initialize(self):
        """Initialize the service"""
        logger.info("Initializing medical information service with OpenFDA API")
        # Pre-load some common medications
        self._load_common_medications()
        
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up medical information service")
        # Clear in-memory cache
        self.drug_database = {}
        
    def get_medical_info(self, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get medical information based on recognized intent
        
        Args:
            intent_data: Dictionary containing intent and slot values
            
        Returns:
            Response with medical information
        """
        try:
            intent = intent_data.get('intent', 'unknown')
            medication = intent_data.get('slots', {}).get('medication', 'generic')
            
            if intent == 'unknown':
                return {
                    'status': 'error',
                    'response': "I'm not sure what you're asking about. Could you please rephrase?",
                    'data': {}
                }
                
            # Route to the appropriate handler based on intent
            if intent == 'GetSideEffects':
                return self._get_side_effects(medication)
            elif intent == 'GetDosageInfo':
                return self._get_dosage_info(medication)
            elif intent == 'GetDrugInteractions':
                return self._get_drug_interactions(medication)
            else:
                # General medication info
                return self._get_general_info(medication)
                
        except Exception as e:
            logger.error(f"Error getting medical info: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'response': "I'm sorry, but I couldn't retrieve that information at the moment.",
                'data': {}
            }
            
    def _load_common_medications(self):
        """Pre-load information about common medications"""
        # This would typically load from a database
        # For demonstration, we'll hardcode a few medications
        self.drug_database = {
            "aspirin": {
                "generic_name": "aspirin",
                "brand_names": ["Bayer", "Ecotrin", "Bufferin"],
                "description": "Pain reliever and fever reducer",
                "side_effects": "Common side effects include stomach irritation, nausea, and increased risk of bleeding.",
                "dosage": "Adults: 325-650 mg every 4-6 hours as needed, not to exceed 4,000 mg per day."
            },
            "ibuprofen": {
                "generic_name": "ibuprofen",
                "brand_names": ["Advil", "Motrin", "Nurofen"],
                "description": "Nonsteroidal anti-inflammatory drug (NSAID)",
                "side_effects": "Common side effects include stomach pain, heartburn, nausea, and dizziness.",
                "dosage": "Adults: 200-400 mg every 4-6 hours as needed, not to exceed 1,200 mg per day."
            }
        }
            
    def _get_side_effects(self, medication: str) -> Dict[str, Any]:
        """Get side effects for a specific medication"""
        medication = medication.lower()
        
        # Check in-memory database first
        if medication in self.drug_database:
            return {
                'status': 'success',
                'response': f"Side effects of {medication}: {self.drug_database[medication]['side_effects']}",
                'data': {
                    'medication': medication,
                    'side_effects': self.drug_database[medication]['side_effects']
                }
            }
            
        # Query OpenFDA API if not in local database
        try:
            url = f"{self.api_base_url}/label.json?search=openfda.generic_name:{medication}&limit=1"
            if self.openfda_api_key:
                url += f"&api_key={self.openfda_api_key}"
                
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get('results') and len(data['results']) > 0:
                    side_effects = data['results'][0].get('adverse_reactions', ["Information not available"])[0]
                    return {
                        'status': 'success',
                        'response': f"Side effects of {medication}: {side_effects}",
                        'data': {
                            'medication': medication,
                            'side_effects': side_effects
                        }
                    }
                    
            # Fallback response if not found
            return {
                'status': 'success',
                'response': f"I couldn't find specific side effect information for {medication}. Please consult with a healthcare professional.",
                'data': {}
            }
            
        except Exception as e:
            logger.error(f"Error fetching side effects from OpenFDA: {str(e)}")
            return {
                'status': 'error',
                'response': "I'm sorry, but I couldn't retrieve side effect information at the moment.",
                'data': {}
            }
            
    def _get_dosage_info(self, medication: str) -> Dict[str, Any]:
        """Get dosage information for a specific medication"""
        medication = medication.lower()
        
        # Check in-memory database first
        if medication in self.drug_database:
            return {
                'status': 'success',
                'response': f"Dosage information for {medication}: {self.drug_database[medication]['dosage']}",
                'data': {
                    'medication': medication,
                    'dosage': self.drug_database[medication]['dosage']
                }
            }
            
        # Fallback response
        return {
            'status': 'success',
            'response': f"I couldn't find specific dosage information for {medication}. Please consult with a healthcare professional for appropriate dosing.",
            'data': {}
        }
        
    def _get_drug_interactions(self, medication: str) -> Dict[str, Any]:
        """Get drug interaction information"""
        # This would typically query a drug interaction database
        return {
            'status': 'success',
            'response': f"For information about drug interactions with {medication}, please consult with your pharmacist or healthcare provider.",
            'data': {}
        }
        
    def _get_general_info(self, medication: str) -> Dict[str, Any]:
        """Get general information about a medication"""
        medication = medication.lower()
        
        # Check in-memory database first
        if medication in self.drug_database:
            info = self.drug_database[medication]
            brand_names = ", ".join(info['brand_names'])
            response = f"{medication.capitalize()} ({brand_names}): {info['description']}"
            return {
                'status': 'success',
                'response': response,
                'data': info
            }
            
        # Fallback response
        return {
            'status': 'success',
            'response': f"I don't have detailed information about {medication} in my database yet.",
            'data': {}
        } 