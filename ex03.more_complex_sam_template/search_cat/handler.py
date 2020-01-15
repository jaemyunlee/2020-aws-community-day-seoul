import os
from application import DynamoDBCatRepository
from lambda_logger import logger
import boto3

session = boto3.client('dynamodb')
if os.getenv('ENV') == 'test':
    session = boto3.client('dynamodb', endpoint_url='http://dynamodb:8000')


def lambda_handler(event, context):
    logger.debug(event)
    query__param = event.get('queryStringParameters')
    repository = DynamoDBCatRepository(session, os.environ['TABLE_NAME'])
    cat = repository.get(**query__param)

    return {
        'statusCode': 200,
        'body': cat.json()
    }
