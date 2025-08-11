from fastapi import Request, HTTPException
from typing import Optional
import logging

logger = logging.getLogger(__name__)

async def extract_user_api_key(request: Request) -> str:
    """
    요청에서 사용자 API Key를 추출합니다.
    X-User-API-Key 헤더에서 추출하며, 없으면 에러를 발생시킵니다.
    """
    try:
        user_api_key = request.headers.get("X-User-API-Key")
        
        if not user_api_key:
            raise ValueError("사용자 OpenAI API Key가 필요합니다. 헤더에 'X-User-API-Key'를 포함해주세요.")
        
        # 기본적인 형식 검증만 (sk-로 시작하는지)
        if not user_api_key.startswith("sk-"):
            raise ValueError("OpenAI API Key는 'sk-'로 시작해야 합니다.")
        
        logger.info(f"사용자 API Key 사용: {user_api_key[:10]}...")
        return user_api_key
        
    except Exception as e:
        logger.error(f"API Key 추출 중 오류: {str(e)}")
        raise e

def validate_api_key(api_key: str) -> bool:
    """
    API Key의 형식을 검증합니다.
    """
    if not api_key:
        return False
    
    # OpenAI API Key 형식 검증
    if not api_key.startswith("sk-") or len(api_key) != 51:
        return False
    
    return True 