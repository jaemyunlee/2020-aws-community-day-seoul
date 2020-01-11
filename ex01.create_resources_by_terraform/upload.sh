aws s3api create-bucket \
--bucket=aws-community-day-example \
--region=ap-northeast-2 \
--create-bucket-configuration LocationConstraint=ap-northeast-2
aws s3 cp example.zip s3://aws-community-day-example/v1.0.0/example.zip