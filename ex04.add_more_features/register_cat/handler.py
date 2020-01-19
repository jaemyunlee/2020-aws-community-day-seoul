import json
import os
from application import Cat, DynamoDBCatRepository
from lambda_logger import logger
import boto3

session = boto3.client('dynamodb')
if os.getenv('ENV') == 'test':
    session = boto3.client('dynamodb', endpoint_url='http://dynamodb:8000')


def lambda_handler(event, context):
    logger.debug(event)
    body = json.loads(event.get('body'))
    cat = Cat(**body)
    repository = DynamoDBCatRepository(session, os.environ['TABLE_NAME'])
    repository.add(cat)

    return {
        'statusCode': 201
    }
