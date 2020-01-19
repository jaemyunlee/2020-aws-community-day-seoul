# AWS SAM으로 서버리스 아키텍처 운영하기 <!-- omit in toc -->

2020 AWS Community Day의 발표 중 하나인 "AWS SAM으로 서버리스 아키텍쳐 운영하기"의 샘플코드입니다.

**예제 코드는 다음 환경에서 작성되고 테스트되었습니다.**

- MacOS 
- awscli v1.16.214
- terraform v0.12.19
- aws-sam-cli v0.39.0

**Table of contents**
- [ex01.create_resources_by_terraform](#ex01createresourcesbyterraform)
  - [압축된 lambda source code를 S3에 저장](#%ec%95%95%ec%b6%95%eb%90%9c-lambda-source-code%eb%a5%bc-s3%ec%97%90-%ec%a0%80%ec%9e%a5)
  - [Terraform으로 배포](#terraform%ec%9c%bc%eb%a1%9c-%eb%b0%b0%ed%8f%ac)
- [ex02.create_resources_by_sam](#ex02createresourcesbysam)
  - [AWS SAM으로 배포](#aws-sam%ec%9c%bc%eb%a1%9c-%eb%b0%b0%ed%8f%ac)
- [ex03.more_complex_sam_template](#ex03morecomplexsamtemplate)
  - [sam local command로 로컬에서 테스트하기](#sam-local-command%eb%a1%9c-%eb%a1%9c%ec%bb%ac%ec%97%90%ec%84%9c-%ed%85%8c%ec%8a%a4%ed%8a%b8%ed%95%98%ea%b8%b0)
- [ex04.add_more_features](#ex04addmorefeatures)
  - [Parameter Store에 Parameter 추가](#parameter-store%ec%97%90-parameter-%ec%b6%94%ea%b0%80)
  - [Nested Stack 추가](#nested-stack-%ec%b6%94%ea%b0%80)
- [ex05.pipeline](#ex05pipeline)
  - [cfn-lint custom rule 만들기](#cfn-lint-custom-rule-%eb%a7%8c%eb%93%a4%ea%b8%b0)
  - [Taskcat으로 테스트하기](#taskcat%ec%9c%bc%eb%a1%9c-%ed%85%8c%ec%8a%a4%ed%8a%b8%ed%95%98%ea%b8%b0)

## ex01.create_resources_by_terraform

간단하게 Lambda를 Terraform으로 배포하는 예제입니다.

### 압축된 lambda source code를 S3에 저장

lambda source code를 압축한 `example.zip`를 s3에 upload합니다.

`bash upload.sh`

`ex01.create_resources_by_terraform/upload.sh`
```
aws s3api create-bucket \
--bucket=aws-community-day-example \
--region=ap-northeast-2 \
--create-bucket-configuration LocationConstraint=ap-northeast-2
aws s3 cp example.zip s3://aws-community-day-example/v1.0.0/example.zip
```

### Terraform으로 배포

Terraform으로 배포합니다.

`bash deploy.sh`

`ex01.create_resources_by_terraform/deploy.sh`
```
terraform init
terraform apply -auto-approve
```

## ex02.create_resources_by_sam

이번에는 `ex01.create_resources_by_terraform`에서 S3에 업로드한 `example.zip`을 재사용하여 AWS SAM으로 배포해보는 예제입니다.

### AWS SAM으로 배포

AWS SAM으로 배포합니다.

`bash deploy.sh`

`ex02.create_resources_by_sam/deploy.sh`
```
aws s3api create-bucket \
--bucket=aws-community-day-example-stack \
--region=ap-northeast-2 \
--create-bucket-configuration LocationConstraint=ap-northeast-2
sam deploy \
--stack-name aws-community-day-example-stack \
--capabilities CAPABILITY_IAM --region=ap-northeast-2
```

## ex03.more_complex_sam_template

API Gateway, Lambda, DynamoDB로 구성된 example application을 SAM Template로 배포하는 예제입니다.

application에서 필요한 python package들을 layer로 사용할 경로에 설치합니다.

```
cd ex03.more_complex_sam_template/application/python
python -r requirements.txt -t .
```

### sam local command로 로컬에서 테스트하기

`sam local command`로 로컬에서 테스트를 할 수 있습니다. DynamoDB local과 localstack을 사용하여 테스트를 합니다. 먼저 `docker-compose`로 container를 실행합니다.

```
cd ex03.more_complex_sam_template/local_test
docker-compose up
```

`sam local start-api`를 통해서 `/cat/`으로 `HTTP GET`과 `HTTP POST`를 request하여 테스트해 볼 수 있습니다.

`bash start-api.sh`

`ex03.more_complex_sam_template/start-api.sh`
```
AWS_ACCESS_KEY_ID=foo AWS_SECRET_ACCESS_KEY=bar AWS_DEFAULT_REGION=ap-northeast-2 \
sam local start-api --docker-network=local_test_my_network
```

다이나모 스트림을 통해서 invoke되는 `SendMessage` Lambda는 `sam local invoke`를 통해서 테스트해 볼 수 있습니다.

`bash invoke-event.sh`

`ex03.more_complex_sam_template/invoke-event.sh`
```
sam local invoke --event ./test/dynamodb_stream_event.json SendMessage
```

## ex04.add_more_features

`AWS System Manager Parameter Store`와 쉽게 연동되는 것과 `NestedStack`를 사용하는 것을 보여주는 간단한 예제입니다.

### Parameter Store에 Parameter 추가

`AWS cli`를 통해서 `Parameter`를 추가합니다.

```
$ aws ssm put-parameter --name theLaziestCat --type String --value "Durian" --region ap-northeast-2
{
    "Version": 1
}
```

SAM Template에 Parameter를 추가하고 `AWS System Manager Parameter Store`로부터 값을 가져오도록 설정합니다.

`ex04.add_more_features/template.yaml`
```
LazyCat:
    Type: 'AWS::SSM::Parameter::Value<String>'
    Default: theLaziestCat
```

### Nested Stack 추가

간단하게 Cloudwatch Log Group을 생성하는 Cloudformation Template를 작성하였습니다.

`ex04.add_more_features/nestedStack.yaml`
```
AWSTemplateFormatVersion: "2010-09-09"
Parameters:
  LambdaName:
    Type: String
Resources: 
  LambdaLog:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/lambda/${LambdaName}"
      RetentionInDays: 3
```

SAM Template에서 해당 Template를 참조해서 `Nested Stack`을 만듭니다.

`ex04.add_more_features/template.yaml`
```
RegisterCatLogGroup:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: ./nestedStack.yaml
      Parameters:
        LambdaName: !Join ["-", [example, !Ref Environment, register, cat]]
SearchCatLogGroup:
    Type: AWS::CloudFormation::Stack
    Properties:
        TemplateURL: ./nestedStack.yaml
        Parameters:
        LambdaName: !Join ["-", [example, !Ref Environment, search, cat]]
```

## ex05.pipeline

`cfn-lint`와 `TaskCat`를 사용하는 예제입니다.

### cfn-lint custom rule 만들기

```
pip install cfn-lint==0.26.2
```

custom rule을 만들어서 `DynamoDB` resource의 `BillingMode`를 `PAY_PER_REQUEST`가 아니면 에러 메세지를 보여주도록 합니다.

template.yaml에서 DynamoDB의 BillingMode를 `PROVISIONED`로 설정하였습니다.

`ex05.pipeline/template.yaml`
```
CatTable:
    Type: 'AWS::DynamoDB::Table'
    Condition: DoNotCreateOnLocal
    Properties:
      TableName: !FindInMap [Config, !Ref Environment, TableName]
      BillingMode: PROVISIONED
      AttributeDefinitions:
        - AttributeName: name
          AttributeType: S
      KeySchema:
        - KeyType: HASH
          AttributeName: name
      StreamSpecification:
        StreamViewType: NEW_IMAGE
```

cfn-lint command를 실행하면 아래처럼 에러 메세지를 확인할 수 있습니다.

```
cfn-lint -i W

E9001 Only PAY_PER_REQUEST is allowed
template.yaml:168:7
```

`.cfnlintrc`에 `lint_custom_rules`의 `LimitedDynamoDBBillingMode.py`를 추가하도록 설정하였습니다.

`ex05.pipeline/.cfnlintrc`
```
templates:
- template.yaml
append_rules:
- lint_custom_rules/
```

### Taskcat으로 테스트하기

```
pip install taskcat==0.9.8
```

template.yaml에서 DynamoDB의 BillingMode를 `PAY_PER_REQUEST`로 변경합니다.

sam build & sam package 명령어로 `packaged.yaml`를 생성합니다.

```
sam build
sam package --s3-bucket aws-community-day-example-stack \
--output-template-file packaged.yaml --region=ap-northeast-2
```

`taskcat test run`

위의 명령어를 실행하면 실제로 Stack을 생성하고 결과리포트를 `taskcat_outputs` 폴더에 생성합니다. `.taskcat.yml`으로 여러 regions에 stack 생성해서 테스트하도록 설정할 수도 있습니다.

`ex05.pipeline/.taskcat.yml`
```
project:
  name: my-cfn-project
  regions:
  - ap-northeast-2
tests:
  default:
    template: packaged.yaml
```