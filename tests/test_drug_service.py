from orchestration.private_apis.drug_service import DrugService
from service_implementations.vendor.openfda_service import OpenFDAService

def test_get_side_effects():
    class MockOpenFDAService:
        def get_drug_side_effects(self, drug_name):
            return ['nausea', 'dizziness'] if drug_name == 'ibuprofen' else []
    
    drug_service = DrugService(openfda_service=MockOpenFDAService())
    result = drug_service.get_side_effects('ibuprofen')
    assert result == ['nausea', 'dizziness']