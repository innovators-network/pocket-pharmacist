import requests

from typing import override

from core.services.interfaces import MedicalInfoService
from core.types.intents import Intent, DrugSideEffectsIntent, DrugDosageIntent, DrugInteractionsIntent, DrugWarningsIntent

from core.services.interfaces import MedicalInfo, MedicalInfoResponse, MedicalInfoError

class OpenFDAMedicalInfoService(MedicalInfoService):

    def __init__(self, config = {}):
        self.fda_api_url = config.get("fda_api_url", "https://api.fda.gov")

    @override
    def initialize(self):
        pass

    @override
    def cleanup(self):
        pass

    @override
    def get_medical_info(self, intent: Intent) -> MedicalInfoResponse:
        try:
            return self._get_medical_info(intent)
        except Exception as e:
            return MedicalInfoError(error=f"Error fetching medical information: {e}")

    def _get_medical_info(self, intent: Intent) -> MedicalInfoResponse:
        if isinstance(intent, DrugSideEffectsIntent):
            return self._handle_side_effects(intent)
        elif isinstance(intent, DrugDosageIntent):
            return self._handle_dosage(intent)
        elif isinstance(intent, DrugInteractionsIntent):
            return self._handle_interactions(intent)
        elif isinstance(intent, DrugWarningsIntent):
            return self._handle_warnings(intent)
        else:
            raise ValueError(f"Unknown intent type: {type(intent)}")

    def _handle_side_effects(self, intent: DrugSideEffectsIntent) -> MedicalInfoResponse:
        drug_name = intent.drug_name
        resp = requests.get(
            url = f"{self.fda_api_url}/drug/event.json",
            params = {
                "search": f"patient.drug.medicinalproduct:{drug_name}",
                "limit": str(5)
            }
        )

        if not resp.ok:
            return MedicalInfoError(error=f"Couldn't fetch data for {drug_name}.")

        data = resp.json()
        effects = []
        for item in data.get("results", []):
            reactions = item.get("patient", {}).get("reaction", [])
            for r in reactions:
                effects.append(r.get("reactionmeddrapt"))

        unique_effects = list(set(effects))[:6]
        text = f"Some reported side effects of {drug_name} include: " + ', '.join(
            unique_effects) if unique_effects else "No common side effects found."

        return MedicalInfo(
            intent=intent,
            message=text
        )

    def _handle_dosage(self, intent: DrugDosageIntent) -> MedicalInfoResponse:
        drug_name = intent.drug_name
        resp = requests.get(f"{self.fda_api_url}/drug/label.json", params={
            "search": f"openfda.brand_name:{drug_name}",
            "limit": str(1)
        })

        text = "I couldn't find dosage information for that drug."
        if resp.ok and resp.json().get("results"):
            dosage = resp.json()["results"][0].get("dosage_and_administration", [])
            text = f"Recommended dosage for {drug_name}: {dosage[0]}" if dosage else text
        return MedicalInfo(
            intent=intent,
            message=text
        )


    def _handle_warnings(self, intent: DrugWarningsIntent) -> MedicalInfoResponse:
        drug_name = intent.drug_name
        resp = requests.get(f"{self.fda_api_url}/drug/label.json", params={
            "search": f"openfda.brand_name:{drug_name}",
            "limit": str(1)
        })

        text = "No warnings available for that drug."
        if resp.ok and resp.json().get("results"):
            warnings = resp.json()["results"][0].get("warnings_and_cautions", [])
            text = f"Warning for {drug_name}: {warnings[0]}" if warnings else text
        return MedicalInfo(
            intent=intent,
            message=text
        )

    def _handle_interactions(self, intent: DrugInteractionsIntent) -> MedicalInfoResponse:
        drug_name = intent.drug_name
        other_drug = intent.other_drug_name

        resp = requests.get(f"{self.fda_api_url}/drug/label.json", params={
            "search": f"openfda.brand_name:{drug_name}",
            "limit": str(1)
        })

        text = f"I couldn't find known interactions between {drug_name} and {other_drug}."
        if resp.ok and resp.json().get("results"):
            interactions = resp.json()["results"][0].get("drug_interactions", [])
            for i in interactions:
                if other_drug.lower() in i.lower():
                    text = f"Interaction warning: {i}"
                    break
            else:
                if interactions:
                    text = f"{drug_name} may interact with other drugs. Example: {interactions[0]}"

        return MedicalInfo(
            intent=intent,
            message=text
        )

