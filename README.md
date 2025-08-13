# CVPilot

AI 기술을 활용한 학술 커리어 분석 서비스

## 소개

CVPilot은 대학원 진학을 준비하는 학생들을 위한 AI 기반 학술 커리어 분석 플랫폼입니다. CV 분석, 논문 트렌드 분석, 면접 연습 등 다양한 기능을 제공합니다.

## 주요 기능

### 📊 CV 분석
- AI가 CV를 분석하여 강점과 개선점 제시
- 스킬 레이더 차트로 시각화
- PDF, DOCX, TXT 파일 지원

### 📈 논문 트렌드 분석
- 최신 AI/ML 연구 동향 실시간 분석
- 관심 분야별 핫한 주제 파악
- 키워드 기반 트렌드 시각화

### 🔍 논문 비교 분석
- 연구 아이디어와 기존 논문 비교
- 차별화 전략 제시
- 유사도 분석

### 💬 CV 기반 면접 연습
- 면접관 모드: AI가 면접관 역할
- 연습 모드: 모범 답변과 조언 제공
- 맞춤형 질문 생성

### 🎙️ 데일리 논문 팟캐스트
- 최신 논문을 음성으로 요약
- TTS 기술 활용
- 오디오 플레이어 제공

### 🏫 연구실 분석
- 연구실별 연구 분야 분석
- 교수진 프로필 제공
- 연구실 추천

## 기술 스택

### Frontend
- Next.js 14
- TypeScript
- Material-UI
- React Hooks

### Backend
- FastAPI
- Python 3.11
- AWS Lambda
- Docker

### AI/ML
- OpenAI GPT-4
- OpenAI Embedding API
- Supabase (PostgreSQL)

### Infrastructure
- AWS S3 (정적 호스팅)
- AWS CloudFront (CDN)
- AWS ECR (Docker 레지스트리)

## 시작하기

### Prerequisites
- Node.js 18+
- Python 3.11+
- OpenAI API Key

### Frontend 실행
```bash
cd app
npm install
npm run dev
```

### Backend 실행
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 배포

### Frontend 배포
```bash
cd app
./deploy-frontend.sh
```

### Backend 배포
```bash
cd backend
./deploy-lambda.sh
```

## 환경 변수

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=https://your-lambda-url.amazonaws.com
```

### Backend (.env)
```
OPENAI_API_KEY=your-openai-api-key
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

## 프로젝트 구조

```
CVPilot/
├── app/                    # Frontend (Next.js)
│   ├── components/         # React 컴포넌트
│   ├── pages/             # 페이지 컴포넌트
│   ├── hooks/             # Custom Hooks
│   ├── api/               # API 클라이언트
│   └── config/            # 설정 파일
├── backend/               # Backend (FastAPI)
│   ├── app/               # 메인 애플리케이션
│   │   ├── cv_analysis/   # CV 분석 모듈
│   │   ├── paper_trend/   # 논문 트렌드 모듈
│   │   ├── cv_QA/         # CV QA 모듈
│   │   └── shared/        # 공통 모듈
│   └── requirements.txt   # Python 의존성
└── utils/                 # 유틸리티 스크립트
```

## 라이선스

MIT License

## 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

<sub>project owner: WonJune Jang</sub>