aws s3api create-bucket \
--bucket=aws-community-day-example-stack \
--region=ap-northeast-2 \
--create-bucket-configuration LocationConstraint=ap-northeast-2
sam deploy \
--stack-name aws-community-day-example-stack \
--capabilities CAPABILITY_IAM --region=ap-northeast-2