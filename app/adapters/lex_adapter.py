from orchestration.models.entities import ChatbotRequest, ChatbotResponse

def lex_to_orchestration(event):
    """Convert Lex event to orchestration request."""
    intent_name = event['currentIntent']['name']
    slots = event['currentIntent']['slots']
    return ChatbotRequest(intent=intent_name, params=slots)

def orchestration_to_lex(orch_response):
    """Convert orchestration response to Lex format."""
    return {
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': 'Fulfilled',
            'message': {
                'contentType': 'PlainText',
                'content': orch_response.message
            }
        }
    }