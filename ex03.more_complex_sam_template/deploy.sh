sam build
sam package --s3-bucket aws-community-day-example-stack \
--output-template-file packaged.yaml --region=ap-northeast-2
sam deploy --template-file packaged.yaml \
--stack-name aws-community-day-example-stack \
--capabilities CAPABILITY_IAM --region=ap-northeast-2