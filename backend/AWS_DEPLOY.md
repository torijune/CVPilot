# AWS Lambda 배포 가이드 🚀

## 전제 조건

### 1. AWS CLI 설치 및 설정
```bash
# AWS CLI 설치
pip install awscli

# AWS 계정 설정
aws configure
```

### 2. SAM CLI 설치
```bash
# SAM CLI 설치
pip install aws-sam-cli

# 설치 확인
sam --version
```

## 배포 방법

### 방법 1: 자동 배포 스크립트 (추천)

```bash
# 환경 변수 설정
export OPENAI_API_KEY="your_openai_key"
export SUPABASE_URL="your_supabase_url"  
export SUPABASE_KEY="your_supabase_key"

# 배포 실행
chmod +x deploy.sh
./deploy.sh
```

### 방법 2: 수동 배포

```bash
# 1. 빌드
sam build

# 2. 배포
sam deploy \
    --stack-name cvpilot-backend \
    --region ap-northeast-2 \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
        OpenAIApiKey=$OPENAI_API_KEY \
        SupabaseUrl=$SUPABASE_URL \
        SupabaseKey=$SUPABASE_KEY \
    --confirm-changeset
```

## 배포 후 확인

### 1. API Gateway URL 확인
```bash
aws cloudformation describe-stacks \
    --stack-name cvpilot-backend \
    --query 'Stacks[0].Outputs[?OutputKey==`CVPilotApi`].OutputValue' \
    --output text
```

### 2. 헬스체크
```bash
curl https://your-api-id.execute-api.ap-northeast-2.amazonaws.com/prod/health
```

## 비용 예상 💰

### Lambda (월간 예상)
- **무료 티어**: 100만 요청/월, 3.2M GB-초
- **유료**: 요청당 $0.0000002 + 실행시간당 $0.0000166667/GB-초

### API Gateway
- **무료 티어**: 100만 API 호출/월
- **유료**: 100만 호출당 $3.50

### 예상 비용 (월 1만 요청 기준)
- **Lambda**: 거의 무료 (무료 티어 내)
- **API Gateway**: 거의 무료 (무료 티어 내)
- **총 비용**: $0-5/월

## 모니터링

### CloudWatch 로그
```bash
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/cvpilot"
```

### 성능 메트릭
- AWS Lambda 콘솔에서 확인
- CloudWatch 대시보드 생성 가능

## 장점 ✅

1. **비용 효율성**: 사용한 만큼만 지불
2. **자동 스케일링**: 트래픽에 따라 자동 확장
3. **서버 관리 불필요**: 완전 관리형
4. **높은 가용성**: AWS 인프라의 안정성

## 단점 ⚠️

1. **Cold Start**: 첫 요청 시 지연 (1-3초)
2. **실행 시간 제한**: 최대 15분
3. **메모리 제한**: 최대 10GB
4. **AWS 종속성**: 벤더 락인 