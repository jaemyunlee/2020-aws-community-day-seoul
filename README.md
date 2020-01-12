# AWS SAM으로 서버리스 아키텍처 운영하기

2020 AWS Community Day의 발표 중 하나인 "AWS SAM으로 서버리스 아키텍쳐 운영하기"의 샘플코드입니다.

## 안내사항

⚠️**복잡한 구성으로 서버리스 아키텍쳐를 구성할 때 발생하는 Challenge에 대한 해결책은 제시할 수 없습니다**
- API Gateway, Lambda, DynamoDB, SNS, SQS로 구성된 비교적 간단한 시스템에서 활용된 경험을 바탕으로 작성되었습니다. 일부 프로젝트는 Aurora, ElastiCache를 위해서 람다의 VPC설정을 하거나, JWT인증을 위해 Lambda로 Custom Authorizer를 구성하였습니다.

⚠️**Terraform을 자세히 설명하지 않습니다. Terraform을 다양한 측면에서 AWS SAM과 비교하지 않습니다**
- API gateway와 Lambda를 사용하여 Infrastructure as Code를 구성할 경우로 제한하여 Terraform과 비교합니다.
- Terraform과 AWS SAM에 대한 비교는 저의 **제한적인 경험**을 바탕으로한 개인적인 의견입니다.

**예제 코드는 다음 환경에서 작성되고 테스트되었습니다.**
- MacOS 
- awscli v1.16.214
- terraform v0.12.19
- aws-sam-cli v0.39.0

## 나에게 주어진 Challenge
- 짧은 기간에 Serverless로 구성하여 프로젝트가 진행.(API Gateway, Lambda, DynamoDB, SQS, SNS)
- Infrastrucre as Code로 Resource들이 관리되어야 함.
- 기존 AWS ECS로 구성된 서비스들이 존재하고 Terraform으로 작성되어 있었음.

🤔 **Terraform으로 계속 작업을 해야 하는 것일까???**

## Terraform으로 작업을 했을 때

API gateway, Lambda proxy integration를 구성해봅시다. \
[Hashicorp Tutorial Page의 sample code를 사용](https://learn.hashicorp.com/terraform/aws/lambda-api-gateway)

`ex01.create_resources_by_terraform/main.tf`
```
provider "aws" {
    version = "~>2.44"
    region  = "ap-northeast-2"
}

resource "aws_lambda_function" "example" {
    function_name = "ServerlessExample"

    s3_bucket = "aws-community-day-example"
    s3_key    = "v1.0.0/example.zip"
    
    handler = "main.handler"
    runtime = "nodejs10.x"

    role = aws_iam_role.lambda_exec.arn
}

resource "aws_iam_role" "lambda_exec" {
    name = "serverless_example_lambda"

    assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
        "Action": "sts:AssumeRole",
        "Principal": {
            "Service": "lambda.amazonaws.com"
        },
        "Effect": "Allow",
        "Sid": ""
        }
    ]
}
EOF

}

resource "aws_api_gateway_rest_api" "example" {
    name        = "ServerlessExample"
    description = "Terraform Serverless Application Example"
}

resource "aws_api_gateway_method" "proxy_root" {
    rest_api_id   = aws_api_gateway_rest_api.example.id
    resource_id   = aws_api_gateway_rest_api.example.root_resource_id
    http_method   = "GET"
    authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_root" {
    rest_api_id = aws_api_gateway_rest_api.example.id
    resource_id = aws_api_gateway_method.proxy_root.resource_id
    http_method = aws_api_gateway_method.proxy_root.http_method

    integration_http_method = "POST"
    type                    = "AWS_PROXY"
    uri                     = aws_lambda_function.example.invoke_arn
}

resource "aws_api_gateway_deployment" "example" {
    depends_on = [
        # aws_api_gateway_integration.lambda,
        aws_api_gateway_integration.lambda_root,
    ]

    rest_api_id = aws_api_gateway_rest_api.example.id
    stage_name  = "test"
}

resource "aws_lambda_permission" "apigw" {
   statement_id  = "AllowAPIGatewayInvoke"
   action        = "lambda:InvokeFunction"
   function_name = aws_lambda_function.example.function_name
   principal     = "apigateway.amazonaws.com"

   source_arn = "${aws_api_gateway_rest_api.example.execution_arn}/*/*"
}
```

## AWS SAM으로 작업을 했을 때

`ex02.create_resources_by_sam/template.yaml`
```
Transform: "AWS::Serverless-2016-10-31"
Description: "example template"

Resources:
  Api:
    Type: "AWS::Serverless::Api"
    Properties:
      StageName: test
      TracingEnabled: false
      EndpointConfiguration: REGIONAL
  ServerlessExample:
    Type: "AWS::Serverless::Function"
    Properties:
      FunctionName: serverless_example_lambda
      Runtime: nodejs10.x
      Handler: main.handler
      CodeUri:
        Bucket: aws-community-day-example
        Key: v1.0.0/example.zip
      Events:
        PublicApi:
          Type: Api
          Properties:
            Path: /
            Method: GET
            RestApiId: !Ref Api
```

Sample code `ex02.create_resources_by_sam/deploy.sh`를 실행하면 아래처럼 resource들이 생기는 것을 알 수 있습니다. Terraform으로 resource들을 별도로 정의해서 만들어줬지만 SAM Template는 필요한 Resource들을 자동으로 만들어주고 있습니다.

| Operation | ResourceType                |
| --------- | --------------------------- |
| + Add     | AWS::ApiGateway::Deployment |
| + Add     | AWS::ApiGateway::Stage      |
| + Add     | AWS::ApiGateway::RestApi    |
| + Add     | AWS::Lambda::Permission     |
| + Add     | AWS::IAM::Role              |
| + Add     | AWS::Lambda::Function       |

I ♥️ terraform! 

Terraform도 module들을 잘 구성하면 압축해서 이쁘게 사용할 수 있을 것이라 생각을 합니다. [Terraform Registry](https://registry.terraform.io/)에 보면 [lambda-api-gateway](https://registry.terraform.io/modules/techjacker/lambda-api-gateway/aws/1.0.2)와 같이 이미 누군가 만들어진 module들이 존재합니다. 

🤓게으른 개발자

하지만 저는 AWS SAM이 API Gateway와 Lambda로 구성할 때 간단하고 직관적이다고 생각했습니다. `AutoPublishAlias`를 통해서 Lambda version과 alias를 쉽게 설정할 수도 있고, `X-ray`를 연동할 때 `Tracing`를 `Active`로 바꿔주면 되고 `DeploymentPreference`를 통해서 `Canary 배포`를 간단하게 설정할 수 있었습니다. 

## AWS SAM Template

SAM Template에 대한 specification이 잘 정리되어 있습니다. 저 자세한 내용은 [여기서](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md) 확인하세요.

