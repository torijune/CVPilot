#!/bin/bash

# AWS ECR 및 Lambda 배포 스크립트

# 설정
AWS_REGION="us-east-1"
ECR_REPOSITORY_NAME="cvpilot-lambda"
LAMBDA_FUNCTION_NAME="cvpilot-lambda"

echo "🚀 CVPilot Lambda Docker 배포 시작..."

# 1. AWS ECR 로그인
echo "📦 AWS ECR 로그인 중..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com

# 2. ECR 리포지토리 생성 (없는 경우)
echo "🏗️ ECR 리포지토리 확인/생성 중..."
aws ecr describe-repositories --repository-names $ECR_REPOSITORY_NAME --region $AWS_REGION 2>/dev/null || \
aws ecr create-repository --repository-name $ECR_REPOSITORY_NAME --region $AWS_REGION

# 3. ECR URI 가져오기
ECR_URI=$(aws ecr describe-repositories --repository-names $ECR_REPOSITORY_NAME --region $AWS_REGION --query 'repositories[0].repositoryUri' --output text)
IMAGE_TAG="latest"
FULL_IMAGE_URI="$ECR_URI:$IMAGE_TAG"

echo "📸 ECR URI: $FULL_IMAGE_URI"

# 4. Docker 이미지 빌드
echo "🔨 Docker 이미지 빌드 중..."
docker build -f Dockerfile.lambda -t $ECR_REPOSITORY_NAME:$IMAGE_TAG .

# 5. 이미지 태그 설정
echo "🏷️ 이미지 태그 설정 중..."
docker tag $ECR_REPOSITORY_NAME:$IMAGE_TAG $FULL_IMAGE_URI

# 6. ECR에 이미지 푸시
echo "⬆️ ECR에 이미지 푸시 중..."
docker push $FULL_IMAGE_URI

# 7. Lambda 함수 업데이트
echo "🔄 Lambda 함수 업데이트 중..."
aws lambda update-function-code \
    --function-name $LAMBDA_FUNCTION_NAME \
    --image-uri $FULL_IMAGE_URI \
    --region $AWS_REGION

echo "✅ 배포 완료!"
echo "🌐 Lambda Function URL: https://$(aws lambda get-function-url-config --function-name $LAMBDA_FUNCTION_NAME --region $AWS_REGION --query 'FunctionUrl' --output text)" 