from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="FOM2025 Summer Conference Backend",
    description="AI/ML 연구자를 위한 종합 분석 플랫폼",
    version="1.0.0"
)

# CORS 설정 - 모든 도메인 허용 (개발/테스트용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용
    allow_credentials=False,  # credentials는 와일드카드와 함께 사용 불가
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
from app.paper_trend.api.routes.trend_routes import router as trend_router
from app.paper_comparsion.api.routes.comparison_routes import router as comparison_router
from app.cv_analysis.api.routes.cv_routes import router as cv_router
from app.daily_paper_podcast.api.routes.podcast_routes import router as daily_paper_podcast_router
from app.cv_QA.api.routes.cv_qa_routes import router as cv_qa_router
from app.shared.api.routes.lab_search_routes import router as lab_search_router
from app.lab_analysis.api.routes.lab_analysis_routes import router as lab_analysis_router

# 정적 파일 서빙 설정 (오디오 파일용)
# Lambda 환경에서는 /tmp 디렉토리 사용
if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    # Lambda 환경
    temp_dir = "/tmp/temp_audio"
else:
    # 로컬 환경
    temp_dir = os.path.join(os.path.dirname(__file__), "..", "temp_audio")
os.makedirs(temp_dir, exist_ok=True)
app.mount("/audio", StaticFiles(directory=temp_dir), name="audio")

# 라우터 등록
app.include_router(trend_router, prefix="/api/v1/trends", tags=["trends"])
app.include_router(comparison_router, prefix="/api/v1/comparison", tags=["comparison"])
app.include_router(cv_router, prefix="/api/v1/cv", tags=["cv"])
app.include_router(daily_paper_podcast_router, prefix="/api/v1/podcast", tags=["podcast"])
app.include_router(cv_qa_router, prefix="/api/v1/cv-qa", tags=["cv_qa"])
app.include_router(lab_search_router, prefix="/api/v1/labs", tags=["lab_search"])
app.include_router(lab_analysis_router, prefix="/api/v1/lab-analysis", tags=["lab_analysis"])

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "FOM2025 Summer Conference Backend API",
        "version": "1.0.0",
        "features": [
            "Paper Trend Analysis",
            "Paper Comparison", 
            "CV Analysis",
            "CV QA",
            "Daily Paper Podcast",
            "Lab Search",
            "Lab Analysis"
        ],
        "endpoints": {
            "trends": "/api/v1/trends",
            "comparison": "/api/v1/comparison",
            "cv": "/api/v1/cv",
            "podcast": "/api/v1/podcast",
            "labs": "/api/v1/labs",
            "lab_analysis": "/api/v1/lab-analysis"
        }
    }

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy", "service": "fom2025_backend"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 