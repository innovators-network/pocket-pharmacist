from orchestration.private_apis.drug_service import DrugService
from orchestration.models.entities import ChatbotRequest, ChatbotResponse

class ChatbotAPI:
    def __init__(self, drug_service=None):
        self.drug_service = drug_service or DrugService()

    def handle_request(self, request: ChatbotRequest) -> ChatbotResponse:
        """Handle user requests by orchestrating private APIs."""
        if request.intent == 'GetDrugSideEffects':
            drug_name = request.params.get('drugName')
            if not drug_name:
                return ChatbotResponse(message="Please provide a drug name.")
            side_effects = self.drug_service.get_side_effects(drug_name)
            if side_effects:
                message = f"{drug_name} may cause: {', '.join(side_effects)}."
            else:
                message = f"No side effects found for {drug_name}."
        else:
            message = "Sorry, I don’t understand that request."
        return ChatbotResponse(message=message)