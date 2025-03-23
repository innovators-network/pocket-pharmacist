import boto3
import json

def create_lex_bot():
    lex_client = boto3.client('lex-models')

    # Define the intent
    intent = {
        'intentName': 'GetDrugSideEffects',
        'intentVersion': '1'
    }

    # Create the intent
    lex_client.put_intent(
        name='GetDrugSideEffects',
        description='Get side effects of a drug',
        slots=[
            {
                'name': 'drugName',
                'slotType': 'AMAZON.AlphaNumeric',
                'slotConstraint': 'Required',
                'valueElicitationPrompt': {
                    'messages': [
                        {'contentType': 'PlainText', 'content': 'Which drug would you like to know about?'}
                    ],
                    'maxAttempts': 2
                },
                'priority': 1
            }
        ],
        sampleUtterances=[
            'What are the side effects of {drugName}',
            'Tell me about {drugName} side effects',
            'Side effects of {drugName}'
        ],
        fulfillmentActivity={
            'type': 'CodeHook',
            'codeHook': {
                'uri': 'arn:aws:lambda:region:account-id:function:pocket-pharmacist-dev-LexHandler',  # Replace with your Lambda ARN
                'messageVersion': '1.0'
            }
        }
    )

    # Create the bot
    lex_client.put_bot(
        name='PocketPharmacistBot',
        intents=[intent],
        clarificationPrompt={
            'messages': [
                {'contentType': 'PlainText', 'content': 'Sorry, I didn’t understand that. Can you try again?'}
            ],
            'maxAttempts': 2
        },
        abortStatement={
            'messages': [
                {'contentType': 'PlainText', 'content': 'I’m sorry, I can’t assist with that.'}
            ]
        },
        idleSessionTTLInSeconds=300,
        locale='en-US',
        childDirected=False
    )

    print("Lex bot 'PocketPharmacistBot' created successfully.")

if __name__ == '__main__':
    create_lex_bot()