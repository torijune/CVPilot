#!/bin/bash

echo "🚀 CVPilot Google Cloud Run 배포 시작..."

# 설정 변수
PROJECT_ID=${PROJECT_ID:-"cvpilot-project"}
SERVICE_NAME=${SERVICE_NAME:-"cvpilot-backend"}
REGION=${REGION:-"asia-northeast3"}
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# 환경 변수 체크
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY 환경 변수가 필요합니다."
    exit 1
fi

if [ -z "$SUPABASE_URL" ]; then
    echo "❌ SUPABASE_URL 환경 변수가 필요합니다."
    exit 1
fi

if [ -z "$SUPABASE_KEY" ]; then
    echo "❌ SUPABASE_KEY 환경 변수가 필요합니다."
    exit 1
fi

# 프로젝트 설정
gcloud config set project $PROJECT_ID

# API 활성화
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# 빌드 및 배포
echo "🐳 Docker 이미지 빌드..."
docker build -t $IMAGE_NAME .

echo "📦 이미지 푸시..."
docker push $IMAGE_NAME

echo "🚀 Cloud Run 배포..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --timeout 300 \
    --set-env-vars "OPENAI_API_KEY=$OPENAI_API_KEY,SUPABASE_URL=$SUPABASE_URL,SUPABASE_KEY=$SUPABASE_KEY"

echo "✅ 배포 완료!" 