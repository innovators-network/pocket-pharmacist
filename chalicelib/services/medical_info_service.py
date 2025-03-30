"""
Medical Information Service Implementation
Team: Member 3 (Medication/Symptom Data Processing Team)
Responsibilities:
- Process medication and symptom data
- Integrate with OpenFDA API
- Future integration with S3 for additional data
- Handle data validation and formatting

Implementation Notes:
1. Current Implementation:
   - OpenFDA API integration
   - Basic error handling
   - Response formatting

2. TODO:
   - Implement S3 integration:
     * Store additional medical data
     * Implement fallback data retrieval
   - Add data validation layer
   - Implement caching for frequently accessed data
   - Add data versioning support
"""

from typing import Dict, Any, Optional
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MedicalInfoService:
    def __init__(self):
        self.base_url = "https://api.fda.gov/drug"
        self.session = requests.Session()

    def initialize(self):
        """Initialize the service"""
        # No initialization needed for requests.Session()

    def cleanup(self):
        """Cleanup resources"""
        if self.session:
            self.session.close()

    def get_medical_info(
        self, 
        intent_data: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Get medical information based on intent
        Args:
            intent_data: Dictionary containing intent and slots from Lex
            context: Optional context from previous interactions
        Returns:
            Dictionary containing medical information
        """
        try:
            # Get data based on intent
            intent_name = intent_data.get('intent', {}).get('name', '')
            drug_name = intent_data.get('slots', {}).get('drug_name', '')
            
            # Build FDA API query
            search_params = self._build_search_params(intent_name, drug_name)
            endpoint = self._get_endpoint_for_intent(intent_name)
            
            # Get data from FDA
            response = self.session.get(
                f"{self.base_url}/{endpoint}.json",
                params=search_params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._process_fda_response(data, intent_name)
                
            # TODO: Implement S3 fallback here when FDA API fails
            logger.error(f"FDA API error: {response.status_code}")
            return self._create_error_response("Unable to retrieve drug information")

        except Exception as e:
            logger.error(f"Error getting medical info: {str(e)}", exc_info=True)
            return self._create_error_response("An unexpected error occurred")

    def _build_search_params(self, intent_name: str, drug_name: str) -> Dict[str, str]:
        """Build FDA API search parameters"""
        params = {"limit": 1}
        
        # Map intents to FDA search terms
        intent_search_map = {
            "GetDrugSideEffects": "adverse_reactions",
            "GetDrugDosage": "dosage_and_administration",
            "GetDrugInteractions": "drug_interactions",
            "GetDrugWarnings": "boxed_warnings"
        }
        
        if search_term := intent_search_map.get(intent_name):
            params['search'] = f"openfda.brand_name:{drug_name}+AND+_exists_:{search_term}"
            
        return params

    def _get_endpoint_for_intent(self, intent_name: str) -> str:
        """Get FDA API endpoint based on intent"""
        # Currently all intents use the drug label endpoint
        return "label"

    def _process_fda_response(
        self,
        data: Dict[str, Any],
        intent_name: str
    ) -> Dict[str, Any]:
        """Process FDA API response"""
        try:
            if not data.get('results'):
                return self._create_error_response("No results found")

            result = data['results'][0]
            
            return {
                "status": "success",
                "response": self._format_response_by_intent(result, intent_name),
                "metadata": {
                    "drug_name": result.get('openfda', {}).get('brand_name', [None])[0],
                    "timestamp": datetime.utcnow().isoformat(),
                    "data_source": "OpenFDA"
                }
            }

        except Exception as e:
            logger.error(f"Error processing FDA response: {str(e)}", exc_info=True)
            return self._create_error_response("Error processing medical information")

    def _format_response_by_intent(
        self,
        data: Dict[str, Any],
        intent_name: str
    ) -> str:
        """Format response based on intent type"""
        if intent_name == "GetDrugSideEffects":
            effects = data.get('adverse_reactions', [None])[0]
            return f"Side Effects: {effects or 'No information available'}"
        
        elif intent_name == "GetDrugDosage":
            dosage = data.get('dosage_and_administration', [None])[0]
            return f"Dosage Information: {dosage or 'No information available'}"
        
        elif intent_name == "GetDrugInteractions":
            interactions = data.get('drug_interactions', [None])[0]
            return f"Drug Interactions: {interactions or 'No information available'}"
        
        elif intent_name == "GetDrugWarnings":
            warnings = data.get('boxed_warnings', [None])[0]
            return f"Warnings: {warnings or 'No information available'}"
        
        return "Information not available for this query type."

    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "status": "error",
            "message": error_message,
            "response": "Unable to retrieve medical information at this time."
        } 