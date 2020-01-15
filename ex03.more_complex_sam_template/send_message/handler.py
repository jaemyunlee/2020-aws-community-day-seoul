from application import Cat, NewCatMessage, FakeSender
from lambda_logger import logger
from utils import parse_dynamodb_stream_event


def lambda_handler(event, context):
    logger.debug(event)
    for event in event.get('Records'):
        data = parse_dynamodb_stream_event(event)
        if data:
            cat = Cat(**data)
            message = NewCatMessage(cat.name, cat.get_age_level())
            sender = FakeSender(message)
            sender.send()
