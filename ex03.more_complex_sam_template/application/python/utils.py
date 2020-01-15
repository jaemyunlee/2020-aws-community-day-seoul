from dynamodb_json import json_util as dynamodb_json


def parse_dynamodb_stream_event(event):
    data = event.get('dynamodb')
    if data:
        return dynamodb_json.loads(data.get('NewImage'))
    return None
