from typing import List, Dict, Set
import re

class ResearchAreaMapper:
    """연구 분야를 표준화된 카테고리로 매핑하는 클래스"""
    
    # 표준 카테고리 정의
    STANDARD_CATEGORIES = {
        "NLP": [
            "자연어처리", "NLP", "Natural Language Processing", "자연어 처리",
            "텍스트 마이닝", "Text Mining", "언어 모델", "Language Model",
            "기계번역", "Machine Translation", "문장 분석", "Sentiment Analysis",
            "정보 추출", "Information Extraction", "질의응답", "Question Answering",
            "대화 시스템", "Dialogue System", "요약", "Summarization"
        ],
        "Computer Vision": [
            "컴퓨터 비전", "Computer Vision", "이미지 처리", "Image Processing",
            "객체 검출", "Object Detection", "이미지 분할", "Image Segmentation",
            "얼굴 인식", "Face Recognition", "영상 처리", "Video Processing",
            "3D 비전", "3D Vision", "스테레오 비전", "Stereo Vision",
            "시각적 추적", "Visual Tracking", "시각적 SLAM", "Visual SLAM"
        ],
        "Multimodal": [
            "멀티모달", "Multimodal", "멀티모달 학습", "Multimodal Learning",
            "시각-언어", "Vision-Language", "오디오-비전", "Audio-Vision",
            "텍스트-이미지", "Text-Image", "크로스모달", "Cross-modal",
            "멀티미디어", "Multimedia", "시각-언어 모델", "Vision-Language Model"
        ],
        "Machine Learning": [
            "기계학습", "Machine Learning", "딥러닝", "Deep Learning",
            "신경망", "Neural Network", "강화학습", "Reinforcement Learning",
            "지도학습", "Supervised Learning", "비지도학습", "Unsupervised Learning",
            "전이학습", "Transfer Learning", "메타학습", "Meta Learning",
            "적대적 학습", "Adversarial Learning", "앙상블", "Ensemble",
            "최적화", "Optimization", "딥러닝 최적화", "Deep Learning Optimization"
        ]
    }
    
    @classmethod
    def map_research_areas_to_categories(cls, research_areas: List[str]) -> Dict[str, float]:
        """
        연구 분야 리스트를 표준 카테고리로 매핑하고 매칭 점수를 반환
        
        Args:
            research_areas: 연구 분야 리스트
            
        Returns:
            카테고리별 매칭 점수 딕셔너리
        """
        category_scores = {category: 0.0 for category in cls.STANDARD_CATEGORIES.keys()}
        
        for area in research_areas:
            area_lower = area.lower().strip()
            
            for category, keywords in cls.STANDARD_CATEGORIES.items():
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    
                    # 정확한 매칭
                    if area_lower == keyword_lower:
                        category_scores[category] += 1.0
                        break
                    
                    # 부분 매칭 (키워드가 연구 분야에 포함)
                    elif keyword_lower in area_lower:
                        category_scores[category] += 0.8
                        break
                    
                    # 연구 분야가 키워드에 포함
                    elif area_lower in keyword_lower:
                        category_scores[category] += 0.6
                        break
        
        # 점수 정규화 (0-1 범위)
        max_score = max(category_scores.values()) if category_scores.values() else 1
        if max_score > 0:
            for category in category_scores:
                category_scores[category] /= max_score
        
        return category_scores
    
    @classmethod
    def get_primary_category(cls, research_areas: List[str]) -> str:
        """
        연구 분야의 주요 카테고리를 반환
        
        Args:
            research_areas: 연구 분야 리스트
            
        Returns:
            주요 카테고리명
        """
        category_scores = cls.map_research_areas_to_categories(research_areas)
        
        if not category_scores or max(category_scores.values()) == 0:
            return "Other"
        
        return max(category_scores, key=category_scores.get)
    
    @classmethod
    def filter_labs_by_category(cls, labs_data: List[Dict], target_category: str, 
                               min_score: float = 0.3) -> List[Dict]:
        """
        특정 카테고리에 해당하는 연구실들을 필터링
        
        Args:
            labs_data: 연구실 데이터 리스트
            target_category: 타겟 카테고리
            min_score: 최소 매칭 점수
            
        Returns:
            필터링된 연구실 리스트
        """
        filtered_labs = []
        
        # 카테고리명 정규화
        normalized_category = cls._normalize_category_name(target_category)
        
        for lab in labs_data:
            if "research_areas" not in lab:
                continue
                
            category_scores = cls.map_research_areas_to_categories(lab["research_areas"])
            
            # 정규화된 카테고리로 점수 확인
            score = category_scores.get(normalized_category, 0)
            
            if score >= min_score:
                lab_with_score = lab.copy()
                lab_with_score["category_score"] = score
                lab_with_score["all_category_scores"] = category_scores
                filtered_labs.append(lab_with_score)
        
        # 점수순으로 정렬
        filtered_labs.sort(key=lambda x: x["category_score"], reverse=True)
        
        return filtered_labs
    
    @classmethod
    def _normalize_category_name(cls, category: str) -> str:
        """
        카테고리명을 정규화
        
        Args:
            category: 원본 카테고리명
            
        Returns:
            정규화된 카테고리명
        """
        category_lower = category.lower()
        
        # 카테고리 매핑
        category_mapping = {
            "machine learning / deep learning (ml/dl)": "Machine Learning",
            "machine learning / deep learning": "Machine Learning",
            "ml/dl": "Machine Learning",
            "machine learning": "Machine Learning",
            "ml": "Machine Learning",
            "computer vision (cv)": "Computer Vision",
            "computer vision": "Computer Vision",
            "cv": "Computer Vision",
            "natural language processing (nlp)": "NLP",
            "natural language processing": "NLP",
            "nlp": "NLP",
            "multimodal": "Multimodal"
        }
        
        return category_mapping.get(category_lower, category)
    
    @classmethod
    def get_category_statistics(cls, labs_data: List[Dict]) -> Dict[str, int]:
        """
        전체 연구실 데이터에서 카테고리별 통계를 반환
        
        Args:
            labs_data: 연구실 데이터 리스트
            
        Returns:
            카테고리별 연구실 수
        """
        category_counts = {category: 0 for category in cls.STANDARD_CATEGORIES.keys()}
        category_counts["Other"] = 0
        
        for lab in labs_data:
            if "research_areas" not in lab:
                category_counts["Other"] += 1
                continue
                
            primary_category = cls.get_primary_category(lab["research_areas"])
            category_counts[primary_category] += 1
        
        return category_counts 