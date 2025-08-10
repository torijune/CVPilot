import os
from mangum import Mangum
from app.main import app

# Lambda 핸들러 (CORS는 FastAPI에서 처리)
def handler(event, context):
    # Mangum을 통해 FastAPI 앱을 Lambda 호환으로 변환
    asgi_handler = Mangum(app)
    
    # Lambda 이벤트 처리
    response = asgi_handler(event, context)
    
    return response 