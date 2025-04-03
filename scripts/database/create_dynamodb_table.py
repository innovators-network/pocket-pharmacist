"""
Script to create DynamoDB table for medical information
"""

import boto3
import os
from botocore.exceptions import ClientError

def create_table():
    """Create DynamoDB table for medical information"""
    dynamodb = boto3.resource('dynamodb')
    
    table_name = os.environ.get('DYNAMODB_TABLE', 'medical_info')
    
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'N'  # Number type
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        # Wait until the table exists
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print(f"Table {table_name} created successfully!")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table {table_name} already exists.")
        else:
            print(f"Error creating table: {e}")

if __name__ == "__main__":
    create_table() 