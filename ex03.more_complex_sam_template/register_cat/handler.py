import json
import os
from application import Cat, RegisterCat, register_cat 
import boto3

client = boto3.client('dynamodb')
if os.getenv('ENV') == 'test':
    client = boto3.client('dynamodb', endpoint_url='http://dynamodb:8000')
    
def lambda_handler(event, context):
    

    return {
        'statusCode': 200,
        'body': json.dumps({'Hello':'world'})
    }
