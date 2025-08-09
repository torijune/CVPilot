# CVPilot 배포 가이드 🚀

## 1. 백엔드 배포 (Railway)

### 1.1 Railway 가입 및 프로젝트 생성
1. [Railway](https://railway.app) 접속 후 GitHub로 로그인
2. "New Project" → "Deploy from GitHub repo" 선택
3. CVPilot 저장소 선택

### 1.2 백엔드 배포 설정
1. Railway에서 `backend` 폴더를 루트로 설정
2. 환경 변수 설정:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   PORT=8000
   ```

### 1.3 도메인 확인
- Railway에서 자동 생성된 도메인 확인 (예: `https://cvpilot-backend.railway.app`)

## 2. 프론트엔드 배포 (Vercel)

### 2.1 Vercel 가입 및 프로젝트 생성
1. [Vercel](https://vercel.com) 접속 후 GitHub로 로그인
2. "Add New" → "Project" 선택
3. CVPilot 저장소 임포트

### 2.2 빌드 설정
- **Framework Preset**: Next.js
- **Root Directory**: `app`
- **Build Command**: `npm run build`
- **Output Directory**: `.next`

### 2.3 환경 변수 설정
```
NEXT_PUBLIC_API_URL=https://your-railway-backend-url.railway.app
```

## 3. 도메인 설정 (선택사항)

### 3.1 커스텀 도메인 연결
1. Vercel 프로젝트 설정에서 도메인 추가
2. DNS 레코드 설정
3. HTTPS 자동 설정

## 4. 배포 완료 체크리스트 ✅

- [ ] 백엔드 Railway 배포 성공
- [ ] 프론트엔드 Vercel 배포 성공
- [ ] API 연동 테스트
- [ ] CORS 설정 확인
- [ ] 환경 변수 설정 완료
- [ ] 도메인 연결 (선택사항)

## 5. 트러블슈팅

### 5.1 CORS 오류
- Railway 백엔드 URL을 CORS 허용 목록에 추가 확인

### 5.2 API 연결 오류
- 환경 변수 `NEXT_PUBLIC_API_URL` 설정 확인
- 백엔드 `/health` 엔드포인트 접속 테스트

### 5.3 빌드 오류
- `npm install` 후 로컬에서 빌드 테스트
- 의존성 버전 충돌 확인

## 6. 비용 정보 💰

### Railway (백엔드)
- **무료**: 월 $5 크레딧 (충분함)
- **Pro**: 월 $20 (상용 서비스 시)

### Vercel (프론트엔드)
- **무료**: 개인 프로젝트 충분
- **Pro**: 월 $20 (팀/상용 서비스 시)

## 7. 모니터링

### 7.1 로그 확인
- Railway: 대시보드에서 로그 확인
- Vercel: Functions → 로그 확인

### 7.2 성능 모니터링
- Vercel Analytics 활성화
- Railway Metrics 확인 