"""
Script to upload medical information data to DynamoDB
"""

import boto3
import json
import os
import math
from botocore.exceptions import ClientError
from decimal import Decimal

def convert_floats_to_decimals(obj):
    """Recursively convert all float values to Decimal and handle NaN values"""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None  # Replace NaN/Infinity with None (null in DynamoDB)
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimals(i) for i in obj]
    return obj

def upload_data():
    """Upload medical information data to DynamoDB"""
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ.get('DYNAMODB_TABLE', 'medical_info')
    table = dynamodb.Table(table_name)
    
    # Read the JSON data
    json_path = os.path.join('data', 'processed', 'dynamodb_ready_data.json')
    
    # Custom JSON decoder to handle NaN values
    class NaNDecoder(json.JSONDecoder):
        def default(self, obj):
            if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
                return None
            return obj
    
    with open(json_path, 'r', encoding='utf-8') as f:
        # Load JSON but handle NaN values by replacing them with None
        data = json.load(f)
    
    # Process each item and upload to DynamoDB
    for item in data:
        try:
            # Convert all numeric values to Decimal for DynamoDB and handle NaN
            item = convert_floats_to_decimals(item)
            
            # Upload the item
            table.put_item(Item=item)
            print(f"Successfully uploaded item with id: {item['id']}")
            
        except ClientError as e:
            print(f"Error uploading item {item.get('id', 'unknown')}: {e}")
        except Exception as e:
            print(f"Unexpected error uploading item {item.get('id', 'unknown')}: {e}")

if __name__ == "__main__":
    upload_data() 