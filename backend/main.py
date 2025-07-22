from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# .env 환경변수 로드
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'app', '.env'))

# Feature-Sliced Clean Architecture API 라우터 임포트
from app.cv_analysis.api.cv_analysis import router as cv_analysis_router
from app.cv_loader.api.cv import router as cv_loader_router
from app.paper_trend.api.paper_trend import router as paper_trend_router
from app.profess_analysis.api.profess_analysis import router as profess_analysis_router

app = FastAPI(title="Graduate School Recommend Backend", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Feature-Sliced Clean Architecture API 라우터 등록
app.include_router(cv_analysis_router, prefix="/api/v1/cv-analysis")
app.include_router(cv_loader_router, prefix="/api/v1/cv-loader")
app.include_router(paper_trend_router, prefix="/api/v1/paper-trend")
app.include_router(profess_analysis_router, prefix="/api/v1/profess-analysis")

@app.get("/")
async def root():
    return {"message": "Graduate School Recommend Backend API - Feature-Sliced Clean Architecture"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "architecture": "feature-sliced-clean-architecture"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
