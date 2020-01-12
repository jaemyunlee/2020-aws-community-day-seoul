import logging
import logging.config
import json
import os
import traceback

from datetime import datetime


class JSONFormatter:
    def format(self, record):
        json_record = {
            'level': record.levelname,
            'created': datetime.utcfromtimestamp(record.created).strftime("%Y-%m-%dT%H:%M:%S"),
            'region': os.environ.get('AWS_REGION'),
            'function_name': os.environ.get('AWS_LAMBDA_FUNCTION_NAME'),
            'function_mem': os.environ.get('AWS_LAMBDA_FUNCTION_MEMORY_SIZE'),
            'function_version': os.environ.get('AWS_LAMBDA_FUNCTION_VERSION'),
            'runtime': os.environ.get('AWS_EXECUTION_ENV'),
            'log_group_name': os.environ.get('AWS_LAMBDA_LOG_GROUP_NAME'),
            'log_stream_name': os.environ.get('AWS_LAMBDA_LOG_STREAM_NAME'),
            'service': os.environ.get('SERVICE_NAME'),
            'environment': os.environ.get('ENV'),
            'message': record.msg,
            'exc_info': "".join(traceback.format_exception(*record.exc_info)) if record.exc_info else None
        }
        return json.dumps(json_record)


handler = logging.StreamHandler()
handler.formatter = JSONFormatter()
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(os.environ.get('LOGGER_LEVEL', 'INFO'))
logger.propagate = False