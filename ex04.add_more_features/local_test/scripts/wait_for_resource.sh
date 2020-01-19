#!/bin/sh

until AWS_ACCESS_KEY_ID=foo AWS_SECRET_ACCESS_KEY=bar AWS_DEFAULT_REGION=ap-northeast-2 aws --endpoint-url=http://localstack:4576 sqs list-queues; do
  >&2 echo "SQS is unavailable - sleeping"
  sleep 1
done

echo "SQS is now available!"
exec python create_resource.py