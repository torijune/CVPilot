from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="FOM2025 Summer Conference Backend",
    description="AI/ML 연구자를 위한 종합 분석 플랫폼",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
from app.paper_trend.api.routes.trend_routes import router as trend_router
from app.paper_comparsion.api.routes.comparison_routes import router as comparison_router
from app.cv_analysis.api.routes.cv_routes import router as cv_router

# 라우터 등록
app.include_router(trend_router, prefix="/api/v1/trends", tags=["trends"])
app.include_router(comparison_router, prefix="/api/v1/comparison", tags=["comparison"])
app.include_router(cv_router, prefix="/api/v1/cv", tags=["cv"])

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
            "CV Feedback",
            "CV QA",
            "Daily Paper Podcast"
        ],
        "endpoints": {
            "trends": "/api/v1/trends",
            "comparison": "/api/v1/comparison",
            "cv": "/api/v1/cv"
        }
    }

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy", "service": "fom2025_backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 