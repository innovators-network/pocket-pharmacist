import os
import requests

class OpenFDAService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('OPENFDA_API_KEY')
        self.base_url = "https://api.fda.gov/drug/event.json"

    def get_drug_side_effects(self, drug_name: str) -> list:
        """Fetch side effects from OpenFDA."""
        url = f"{self.base_url}?api_key={self.api_key}&search=patient.drug.medicinalproduct:{drug_name}&limit=1"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data.get('results'):
                return [reaction['reactionmeddrapt'] for reaction in data['results'][0]['patient']['reaction']]
            return []
        except Exception as e:
            print(f"OpenFDA error: {str(e)}")
            return []