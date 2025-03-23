from chalice import Chalice
from app.adapters.lex_adapter import lex_to_orchestration, orchestration_to_lex

app = Chalice(app_name='pocket-pharmacist')

@app.lambda_function(name='LexHandler')
def lex_handler(event, context):
    """Thin adapter to integrate Lex with orchestration layer."""
    orch_request = lex_to_orchestration(event)
    orch_response = app.current_request.env['chatbot_api'].handle_request(orch_request)
    return orchestration_to_lex(orch_response)

# Inject chatbot API (for testing flexibility)
app.current_request.env['chatbot_api'] = __import__('orchestration.public_apis.chatbot_api').public_apis.chatbot_api.ChatbotAPI()