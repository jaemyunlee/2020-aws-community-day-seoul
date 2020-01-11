# AWS SAM으로 서버리스 아키텍처 운영하기

2020 AWS Community Day의 발표 중 하나인 "AWS SAM으로 서버리스 아키텍쳐 운영하기"의 샘플코드입니다.

<span class="float-left text-red tooltipped tooltipped-n" aria-label="Does not meet accessibility standards"><%= octicon("alert") %></span>
<div class="text-green mb-2 ml-4">
  복잡한 구성으로 서버리스 아키텍쳐를 구성할 때 발생하는 Challenge에 대한 해결책은 제시할 수 없습니다.
</div>

API Gateway, Lambda, DynamoDB, SNS, SQS로 구성된 간단한 시스템에서 활용된 경험을 바탕으로 작성되었습니다. (일부 프로젝트는 Aurora, ElastiCache를 위해서 람다의 VPC설정을 하거나, JWT인증을 위해 Lambda로 Custom Authorizer를 구성하였습니다) 