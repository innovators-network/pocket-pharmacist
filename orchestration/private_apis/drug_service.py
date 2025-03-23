from service_implementations.vendor.openfda_service import OpenFDAService

class DrugService:
    def __init__(self, openfda_service=None):
        self.openfda_service = openfda_service or OpenFDAService()

    def get_side_effects(self, drug_name: str) -> list:
        """Fetch side effects for a drug using the OpenFDA service."""
        return self.openfda_service.get_drug_side_effects(drug_name)