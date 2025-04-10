import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

import boto3
import json
import time

# Initialize the Lex V2 client with explicit region
lex_client = boto3.client('lexv2-models', region_name='us-east-1')


def delete_bot_if_exists(bot_name):
    """Delete a Lex V2 bot if it exists."""
    try:
        # List all bots to find the bot ID
        response = lex_client.list_bots()
        bot_id = None
        for bot in response.get('botSummaries', []):
            if bot['botName'] == bot_name:
                bot_id = bot['botId']
                break

        if bot_id:
            logger.info(f"Bot '{bot_name}' already exists with ID {bot_id}. Deleting it...")
            lex_client.delete_bot(
                botId=bot_id,
                skipResourceInUseCheck=True
            )
            # Wait for deletion to complete
            time.sleep(5)
            logger.info(f"Bot '{bot_name}' deleted successfully.")
        else:
            logger.info(f"No existing bot named '{bot_name}' found.")
    except Exception as e:
        logger.warning(f"Error deleting bot '{bot_name}': {str(e)}. Proceeding anyway.")


def create_slot_type(bot_id, slot_type_data):
    """Create a custom slot type"""
    response = lex_client.create_slot_type(
        slotTypeName=slot_type_data['name'],
        description='Drug names for PocketPharmacistBot',
        slotTypeValues=[
            {'sampleValue': {'value': enum_val['value']}}
            for enum_val in slot_type_data['enumerationValues']
        ],
        valueSelectionSetting={
            'resolutionStrategy': 'OriginalValue'
        },
        botId=bot_id,
        botVersion='DRAFT',
        localeId='en_US'
    )
    return response['slotTypeId']


def create_slot(bot_id, intent_id, slot_data, slot_type_id):
    """Create a slot and return its ID"""
    response = lex_client.create_slot(
        slotName=slot_data['name'],
        description=f"Slot for {slot_data['name']}",
        slotTypeId=slot_type_id,
        valueElicitationSetting={
            'slotConstraint': slot_data['slotConstraint'],
            'promptSpecification': {
                'messageGroups': [{
                    'message': {
                        'plainTextMessage': {
                            'value': slot_data['valueElicitationPrompt']['messages'][0]['content']
                        }
                    }
                }],
                'maxRetries': slot_data['valueElicitationPrompt']['maxAttempts']
            }
        },
        botId=bot_id,
        botVersion='DRAFT',
        localeId='en_US',
        intentId=intent_id
    )
    return response['slotId']


def create_intent(bot_id, intent_data, slot_type_ids):
    """Create an intent and its slots"""
    # Create the intent without slots
    response = lex_client.create_intent(
        intentName=intent_data['name'],
        description=f"Intent for {intent_data['name']}",
        sampleUtterances=[
            {'utterance': utterance}
            for utterance in intent_data['sampleUtterances']
        ],
        dialogCodeHook={'enabled': False},
        fulfillmentCodeHook={'enabled': False},
        botId=bot_id,
        botVersion='DRAFT',
        localeId='en_US'
    )
    intent_id = response['intentId']

    # Create and associate slots
    slots = intent_data.get('slots', [])
    slot_ids = []
    for slot_data in slots:
        # Get the slotTypeId for the slot's slotType
        slot_type_name = slot_data['slotType']
        slot_type_id = slot_type_ids.get(slot_type_name)
        if not slot_type_id:
            raise ValueError(f"Slot type '{slot_type_name}' not found in slot_type_ids")

        slot_id = create_slot(bot_id, intent_id, slot_data, slot_type_id)
        slot_ids.append({'slotId': slot_id})

    # Update the intent with the slot IDs (if there are any slots)
    if slot_ids:
        lex_client.update_intent(
            intentId=intent_id,
            intentName=intent_data['name'],
            description=f"Intent for {intent_data['name']}",
            sampleUtterances=[
                {'utterance': utterance}
                for utterance in intent_data['sampleUtterances']
            ],
            dialogCodeHook={'enabled': False},
            fulfillmentCodeHook={'enabled': False},
            slotPriorities=[
                {'priority': idx + 1, 'slotId': slot_id['slotId']}
                for idx, slot_id in enumerate(slot_ids)
            ],
            botId=bot_id,
            botVersion='DRAFT',
            localeId='en_US'
        )

    return intent_id


def create_bot(json_data, roleArn):
    """Create the Lex V2 bot with all components"""
    # Create the bot
    bot_response = lex_client.create_bot(
        botName=json_data['botName'],
        description=json_data['description'],
        roleArn=roleArn,
        dataPrivacy={'childDirected': False},
        idleSessionTTLInSeconds=300,
        botTags={'Purpose': 'PharmacyAssistant'}
    )
    bot_id = bot_response['botId']

    # Wait for bot creation
    logger.info(f"Creating bot: {bot_response['botName']}...")
    time.sleep(5)

    # Create locale with corrected voice settings
    try:
        locale_response = lex_client.create_bot_locale(
            botId=bot_id,
            botVersion='DRAFT',
            localeId='en_US',
            nluIntentConfidenceThreshold=0.40,
            voiceSettings={
                'voiceId': 'Joanna'  # Use a supported voice
            }
        )
    except Exception as e:
        logger.warning(f"Failed to set voice settings: {str(e)}. Proceeding without voice.")
        locale_response = lex_client.create_bot_locale(
            botId=bot_id,
            botVersion='DRAFT',
            localeId='en_US',
            nluIntentConfidenceThreshold=0.40
        )

    # Wait for locale creation
    logger.info("Creating locale...")
    time.sleep(10)

    # Create slot types and store their IDs
    slot_type_ids = {}
    for slot_type in json_data['slotTypes']:
        slot_type_id = create_slot_type(bot_id, slot_type)
        slot_type_ids[slot_type['name']] = slot_type_id
        logger.info(f"Created slot type: {slot_type['name']}")
        time.sleep(2)

    # Create intents
    for intent in json_data['intents']:
        intent_id = create_intent(bot_id, intent, slot_type_ids)
        logger.info(f"Created intent: {intent['name']}")
        time.sleep(2)

    return bot_id


def main(role_arn):
    with open('intents.json', 'r') as file:
        bot_data = json.load(file)

    try:
        delete_bot_if_exists(bot_data['botName'])
        bot_id = create_bot(bot_data, ROLE_ARN)
        logger.info(f"Bot created successfully with ID: {bot_id}")
        logger.info("Note: It may take a few minutes for the bot build to complete.")
        logger.info("You can check the status in the AWS Lex V2 console.")
    except Exception as e:
        logger.error(f"Error creating bot: {str(e)}")


# Replace with your actual role ARN
ROLE_ARN = 'arn:aws:iam::985539762803:role/LexV2BotRole_PocketPharmacist'

if __name__ == "__main__":
    main(ROLE_ARN)