"""
AWS Lambda Handler for CVPilot Backend
FastAPI를 Lambda에서 실행하기 위한 핸들러
"""

import json
import os
from mangum import Mangum
from app.main import app

# Lambda 환경 설정
os.environ.setdefault("AWS_LAMBDA_FUNCTION_NAME", "cvpilot-backend")

# Mangum을 사용하여 FastAPI를 Lambda에서 실행
handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    """
    AWS Lambda 엔트리 포인트
    """
    try:
        # API Gateway 이벤트 처리
        return handler(event, context)
    except Exception as e:
        print(f"Lambda execution error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        } 