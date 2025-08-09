# Google Cloud Run용 Dockerfile
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 설정 (Cloud Run은 PORT 환경변수 사용)
ENV PORT=8080

# 헬스체크 (선택사항)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# FastAPI 실행
CMD exec uvicorn app.main:app --host 0.0.0.0 --port $PORT 