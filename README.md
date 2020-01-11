# AWS SAM으로 서버리스 아키텍처 운영하기

2020 AWS Community Day의 발표 중 하나인 "AWS SAM으로 서버리스 아키텍쳐 운영하기"의 샘플코드입니다.

## 안내사항

**복잡한 구성으로 서버리스 아키텍쳐를 구성할 때 발생하는 Challenge에 대한 해결책은 제시할 수 없습니다**
- API Gateway, Lambda, DynamoDB, SNS, SQS로 구성된 비교적 간단한 시스템에서 활용된 경험을 바탕으로 작성되었습니다. 일부 프로젝트는 Aurora, ElastiCache를 위해서 람다의 VPC설정을 하거나, JWT인증을 위해 Lambda로 Custom Authorizer를 구성하였습니다.

**Terraform을 자세히 설명하지 않습니다. Terraform을 다양한 측면에서 AWS SAM과 비교하지 않습니다**
- API gateway와 Lambda를 사용하여 Infrastructure as Code를 구성할 경우로 제한하여 Terraform과 비교합니다.
- Terraform과 AWS SAM에 대한 비교는 저의 제한적인 경험을 바탕으로한 개인적인 의견입니다.

**예제 코드는 다음 환경에서 작성되고 테스트되었습니다.**
- MacOS 
- awscli v1.16.214
- terraform v0.12.19

## 나에게 주어진 Challenge
- 짧은 기간에 서비스를 개발해야 되었기 때문에 Serverless로 구성하여 프로젝트가 진행. (API Gateway, Lambda, DynamoDB, SQS, SNS)
- Infrastrucre as Code로 Resource들이 관리되어야 함.
- 기존 AWS ECS로 구성된 서비스들이 존재하고 Terraform으로 작성되어 있었음.

🤔 **Terraform으로 계속 작업을 해야 하는 것일까???**

## Terraform으로 작업을 했을 때

API gateway, Lambda proxy integration를 구성해보자. \
[Hashicorp Tutorial Page의 sample code를 사용](https://learn.hashicorp.com/terraform/aws/lambda-api-gateway)

Lambda와 Role을 작성하고,

```
resource "aws_lambda_function" "example" {
   function_name = "ServerlessExample"

   s3_bucket = "terraform-serverless-example"
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
```

API gateway와 API gateway의 Resource, Method를 정의한다.

```
resource "aws_api_gateway_rest_api" "example" {
  name        = "ServerlessExample"
  description = "Terraform Serverless Application Example"
}

resource "aws_api_gateway_resource" "proxy" {
   rest_api_id = aws_api_gateway_rest_api.example.id
   parent_id   = aws_api_gateway_rest_api.example.root_resource_id
   path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
   rest_api_id   = aws_api_gateway_rest_api.example.id
   resource_id   = aws_api_gateway_resource.proxy.id
   http_method   = "ANY"
   authorization = "NONE"
}
```

그리고 Lambda를 연결한다.

```
resource "aws_api_gateway_integration" "lambda" {
   rest_api_id = aws_api_gateway_rest_api.example.id
   resource_id = aws_api_gateway_method.proxy.resource_id
   http_method = aws_api_gateway_method.proxy.http_method

   integration_http_method = "POST"
   type                    = "AWS_PROXY"
   uri                     = aws_lambda_function.example.invoke_arn
}
```

```
resource "aws_api_gateway_method" "proxy_root" {
   rest_api_id   = aws_api_gateway_rest_api.example.id
   resource_id   = aws_api_gateway_rest_api.example.root_resource_id
   http_method   = "ANY"
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
```

```
resource "aws_api_gateway_deployment" "example" {
   depends_on = [
     aws_api_gateway_integration.lambda,
     aws_api_gateway_integration.lambda_root,
   ]

   rest_api_id = aws_api_gateway_rest_api.example.id
   stage_name  = "test"
}
```