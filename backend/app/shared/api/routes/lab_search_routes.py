from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional
from pydantic import BaseModel
from ...application.services.lab_search_service import LabSearchService

router = APIRouter()
lab_search_service = LabSearchService()

# Pydantic 모델들
class LabSearchRequest(BaseModel):
    category: Optional[str] = None
    keyword: Optional[str] = None
    university: Optional[str] = None
    min_score: float = 0.3
    limit: int = 50

class LabSearchResponse(BaseModel):
    labs: List[Dict]
    total_count: int
    category: Optional[str] = None
    keyword: Optional[str] = None

class CategoryStatisticsResponse(BaseModel):
    statistics: Dict[str, int]
    total_labs: int

@router.get("/categories", response_model=List[str])
async def get_available_categories():
    """사용 가능한 연구 분야 카테고리 조회"""
    return [
        "Natural Language Processing (NLP)",
        "Computer Vision", 
        "Multimodal",
        "Machine Learning / Deep Learning"
    ]

@router.get("/statistics", response_model=CategoryStatisticsResponse)
async def get_category_statistics():
    """카테고리별 연구실 통계 조회"""
    statistics = lab_search_service.get_category_statistics()
    total_labs = sum(statistics.values())
    
    return CategoryStatisticsResponse(
        statistics=statistics,
        total_labs=total_labs
    )

@router.post("/search", response_model=LabSearchResponse)
async def search_labs(request: LabSearchRequest):
    """연구실 검색"""
    labs = []
    
    if request.category:
        # 카테고리별 검색
        labs = lab_search_service.search_labs_by_category(
            request.category, 
            request.min_score
        )
    elif request.keyword:
        # 키워드 검색
        labs = lab_search_service.search_labs_by_keyword(request.keyword)
    elif request.university:
        # 대학별 검색
        labs = lab_search_service.get_labs_by_university(request.university)
    else:
        # 기본: 모든 연구실 (제한된 수)
        all_labs = lab_search_service.labs_data
        labs = all_labs[:request.limit]
    
    return LabSearchResponse(
        labs=labs,
        total_count=len(labs),
        category=request.category,
        keyword=request.keyword
    )

@router.get("/search/category/{category}")
async def search_labs_by_category(
    category: str,
    min_score: float = Query(0.3, ge=0.0, le=1.0),
    limit: int = Query(50, ge=1, le=100)
):
    """카테고리별 연구실 검색"""
    labs = lab_search_service.search_labs_by_category(category, min_score)
    return {
        "category": category,
        "labs": labs[:limit],
        "total_count": len(labs),
        "min_score": min_score
    }

@router.get("/search/keyword/{keyword}")
async def search_labs_by_keyword(
    keyword: str,
    limit: int = Query(50, ge=1, le=100)
):
    """키워드로 연구실 검색"""
    labs = lab_search_service.search_labs_by_keyword(keyword)
    return {
        "keyword": keyword,
        "labs": labs[:limit],
        "total_count": len(labs)
    }

@router.get("/universities")
async def get_all_universities():
    """모든 대학 목록 조회"""
    universities = lab_search_service.get_all_universities()
    return {
        "universities": universities,
        "total_count": len(universities)
    }

@router.get("/universities/{university_name}/labs")
async def get_labs_by_university(university_name: str):
    """특정 대학의 연구실 목록 조회"""
    labs = lab_search_service.get_labs_by_university(university_name)
    return {
        "university": university_name,
        "labs": labs,
        "total_count": len(labs)
    }

@router.get("/labs/{professor_name}")
async def get_lab_details(
    professor_name: str,
    university: Optional[str] = None
):
    """특정 연구실 상세 정보 조회"""
    lab = lab_search_service.get_lab_details(professor_name, university)
    
    if not lab:
        raise HTTPException(
            status_code=404, 
            detail=f"연구실을 찾을 수 없습니다: {professor_name}"
        )
    
    return lab

@router.get("/recommendations/{category}")
async def get_recommended_labs(
    category: str,
    limit: int = Query(10, ge=1, le=20)
):
    """특정 카테고리의 추천 연구실 조회"""
    labs = lab_search_service.get_recommended_labs(category, limit)
    return {
        "category": category,
        "recommended_labs": labs,
        "total_count": len(labs)
    }

@router.get("/health")
async def health_check():
    """헬스체크"""
    return {
        "status": "healthy",
        "service": "lab_search",
        "total_labs": len(lab_search_service.labs_data)
    } 