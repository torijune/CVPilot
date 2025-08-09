#!/bin/bash

# CVPilot AWS Lambda 배포 스크립트
echo "🚀 CVPilot AWS Lambda 배포 시작..."

# 필수 환경 변수 체크
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY 환경 변수가 설정되지 않았습니다."
    exit 1
fi

if [ -z "$SUPABASE_URL" ]; then
    echo "❌ SUPABASE_URL 환경 변수가 설정되지 않았습니다."
    exit 1
fi

if [ -z "$SUPABASE_KEY" ]; then
    echo "❌ SUPABASE_KEY 환경 변수가 설정되지 않았습니다."
    exit 1
fi

# AWS CLI 및 SAM CLI 설치 확인
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI가 설치되지 않았습니다."
    echo "   설치: pip install awscli"
    exit 1
fi

if ! command -v sam &> /dev/null; then
    echo "❌ SAM CLI가 설치되지 않았습니다."
    echo "   설치: pip install aws-sam-cli"
    exit 1
fi

# 스택 이름 설정
STACK_NAME=${STACK_NAME:-"cvpilot-backend"}
REGION=${AWS_REGION:-"ap-northeast-2"}  # 서울 리전

echo "📦 SAM 빌드 중..."
sam build

if [ $? -ne 0 ]; then
    echo "❌ SAM 빌드 실패"
    exit 1
fi

echo "🚀 SAM 배포 중..."
sam deploy \
    --stack-name $STACK_NAME \
    --region $REGION \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
        OpenAIApiKey=$OPENAI_API_KEY \
        SupabaseUrl=$SUPABASE_URL \
        SupabaseKey=$SUPABASE_KEY \
    --confirm-changeset

if [ $? -eq 0 ]; then
    echo "✅ 배포 완료!"
    echo "📊 스택 정보:"
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`CVPilotApi`].OutputValue' \
        --output text
else
    echo "❌ 배포 실패"
    exit 1
fi 