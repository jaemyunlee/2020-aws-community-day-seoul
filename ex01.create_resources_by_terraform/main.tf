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