#!/usr/bin/env python3
"""
CVPilot Backend Application Entry Point
Railway 배포를 위한 메인 실행 파일
"""

import os
import sys

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app

# Vercel의 경우 app을 직접 export
handler = app

if __name__ == "__main__":
    import uvicorn
    
    # 환경 변수에서 포트 가져오기 (Railway는 PORT 환경 변수 사용)
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting CVPilot Backend on {host}:{port}")
    print(f"📍 Environment: {'Production' if os.getenv('RAILWAY_ENVIRONMENT') else 'Development'}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,  # 프로덕션에서는 reload 비활성화
        access_log=True
    ) 