import json
import os
from mangum import Mangum
from app.main import app

# Mangum 핸들러 생성
handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    """
    CVPilot FastAPI 앱을 위한 Lambda 핸들러
    """
    try:
        # 요청 정보 로깅
        print(f"Event: {json.dumps(event)}")
        print(f"Context: {context}")
        
        # Mangum을 통해 FastAPI 앱 실행
        return handler(event, context)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': '*'
            },
            'body': json.dumps({
                "error": str(e),
                "message": "Internal server error in CVPilot API"
            })
        } 