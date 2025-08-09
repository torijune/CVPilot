# Google Cloud Run 배포 가이드 🚀

## 사전 준비

### 1. Google Cloud Platform 계정 생성
1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. 결제 계정 설정 (무료 크레딧 $300 제공)

### 2. Google Cloud CLI 설치
```bash
# macOS (Homebrew)
brew install google-cloud-sdk

# 또는 직접 다운로드
curl https://sdk.cloud.google.com | bash

# 설치 확인
gcloud --version
```

### 3. Docker 설치
```bash
# macOS (Homebrew)
brew install docker

# 또는 Docker Desktop 다운로드
# https://www.docker.com/products/docker-desktop
```

### 4. 인증 설정
```bash
# Google Cloud 로그인
gcloud auth login

# Docker 인증 설정
gcloud auth configure-docker
```

## 배포 방법

### 방법 1: 자동 배포 스크립트 (추천) ⚡

```bash
# 1. 환경 변수 설정
export PROJECT_ID="your-gcp-project-id"
export OPENAI_API_KEY="your_openai_key"
export SUPABASE_URL="your_supabase_url"
export SUPABASE_KEY="your_supabase_key"

# 2. 배포 실행
cd backend
chmod +x deploy-gcp.sh
./deploy-gcp.sh
```

### 방법 2: 수동 배포 🔧

```bash
# 1. 프로젝트 설정
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# 2. API 활성화
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# 3. Docker 이미지 빌드
docker build -t gcr.io/$PROJECT_ID/cvpilot-backend .

# 4. 이미지 푸시
docker push gcr.io/$PROJECT_ID/cvpilot-backend

# 5. Cloud Run 배포
gcloud run deploy cvpilot-backend \
    --image gcr.io/$PROJECT_ID/cvpilot-backend \
    --region asia-northeast3 \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --timeout 300 \
    --set-env-vars "OPENAI_API_KEY=$OPENAI_API_KEY,SUPABASE_URL=$SUPABASE_URL,SUPABASE_KEY=$SUPABASE_KEY"
```

### 방법 3: GitHub Actions 자동 배포 (고급) 🔄

GitHub Actions를 사용한 자동 배포 설정:

```yaml
# .github/workflows/deploy-gcp.yml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]
    paths: ['backend/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - id: 'auth'
        uses: 'google-github-actions/auth@v1'
        with:
          credentials_json: '${{ secrets.GCP_SA_KEY }}'
          
      - name: 'Set up Cloud SDK'
        uses: 'google-github-actions/setup-gcloud@v1'
        
      - name: 'Deploy to Cloud Run'
        run: |
          cd backend
          gcloud run deploy cvpilot-backend \
            --source . \
            --region asia-northeast3 \
            --allow-unauthenticated
```

## 배포 후 확인

### 1. 서비스 URL 확인
```bash
gcloud run services describe cvpilot-backend \
    --region asia-northeast3 \
    --format 'value(status.url)'
```

### 2. 헬스체크
```bash
curl https://your-service-url.run.app/health
```

### 3. API 테스트
```bash
# 루트 엔드포인트
curl https://your-service-url.run.app/

# 특정 API 테스트
curl https://your-service-url.run.app/api/v1/lab-analysis/fields
```

## 비용 분석 💰

### Cloud Run 요금 (2024년 기준)
- **CPU**: vCPU 시간당 $0.00002400
- **메모리**: GB 시간당 $0.00000250  
- **요청**: 백만 요청당 $0.40
- **무료 티어**: 월 200만 요청, 36만 vCPU-초, 80만 GB-초

### 예상 비용 (월 1만 요청, 평균 5초 실행)
- **요청**: $0.004 (1만 요청)
- **CPU**: $0.33 (1 vCPU × 5초 × 1만 요청)
- **메모리**: $0.28 (2GB × 5초 × 1만 요청)
- **총계**: 약 $0.61/월 (무료 티어 내)

## 모니터링 & 관리 📊

### 1. 로그 확인
```bash
# 실시간 로그
gcloud logging read "resource.type=cloud_run_revision" --follow

# 특정 서비스 로그
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=cvpilot-backend"
```

### 2. 메트릭 확인
- Google Cloud Console → Cloud Run → cvpilot-backend
- 요청 수, 지연시간, 오류율 등 확인

### 3. 트래픽 분할 (무중단 배포)
```bash
# 새 버전에 50% 트래픽 할당
gcloud run services update-traffic cvpilot-backend \
    --to-revisions=cvpilot-backend-00002-abc=50,cvpilot-backend-00001-xyz=50
```

## 장점 ✅

1. **빠른 Cold Start**: 1초 미만
2. **무제한 실행시간**: 3600초 (1시간)
3. **자동 스케일링**: 0 → 1000 인스턴스
4. **완전 관리형**: 서버 관리 불필요
5. **비용 효율적**: 사용한 만큼만 지불
6. **실무 표준**: 많은 기업에서 사용

## 단점 ⚠️

1. **Google Cloud 종속**: 벤더 락인
2. **Cold Start 존재**: AWS Lambda보다는 빠름
3. **인스턴스 제한**: 최대 1000개
4. **네트워킹 제한**: VPC 연결에 추가 설정 필요

## 트러블슈팅 🔧

### 빌드 실패
```bash
# 로그 확인
gcloud builds log [BUILD_ID]

# 로컬 테스트
docker build -t test-image .
docker run -p 8080:8080 test-image
```

### 메모리 부족
```bash
# 메모리 증가
gcloud run services update cvpilot-backend \
    --memory 4Gi \
    --region asia-northeast3
```

### 환경 변수 문제
```bash
# 환경 변수 확인
gcloud run services describe cvpilot-backend \
    --region asia-northeast3 \
    --format 'value(spec.template.spec.template.spec.containers[0].env[].name,spec.template.spec.template.spec.containers[0].env[].value)'
``` 