import os
from mangum import Mangum
from app.main import app

# Lambda 핸들러 (CORS 헤더 추가)
def handler(event, context):
    # Mangum을 통해 FastAPI 앱을 Lambda 호환으로 변환
    asgi_handler = Mangum(app)
    
    # Lambda 이벤트 처리
    response = asgi_handler(event, context)
    
    # CORS 헤더 추가
    if isinstance(response, dict) and 'headers' in response:
        response['headers'].update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
        })
    elif isinstance(response, dict) and 'multiValueHeaders' in response:
        response['multiValueHeaders'].update({
            'Access-Control-Allow-Origin': ['*'],
            'Access-Control-Allow-Methods': ['GET, POST, PUT, DELETE, OPTIONS'],
            'Access-Control-Allow-Headers': ['Content-Type', 'Authorization', 'X-API-Key'],
        })
    
    return response 