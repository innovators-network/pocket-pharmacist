from orchestration.public_apis.chatbot_api import ChatbotAPI
from orchestration.models.entities import ChatbotRequest, ChatbotResponse

def test_get_drug_side_effects():
    class MockDrugService:
        def get_side_effects(self, drug_name):
            return ['nausea', 'dizziness'] if drug_name == 'ibuprofen' else []
    
    chatbot_api = ChatbotAPI(drug_service=MockDrugService())
    request = ChatbotRequest(intent='GetDrugSideEffects', params={'drugName': 'ibuprofen'})
    response = chatbot_api.handle_request(request)
    assert response.message == "ibuprofen may cause: nausea, dizziness."