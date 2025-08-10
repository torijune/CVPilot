from typing import List, Dict, Set
import re

class ResearchAreaMapper:
    """연구 분야를 표준화된 카테고리로 매핑하는 클래스"""
    
    # 표준 카테고리 정의 (확장된 키워드)
    STANDARD_CATEGORIES = {
        "NLP": [
            # 기본 키워드
            "자연어처리", "NLP", "Natural Language Processing", "자연어 처리",
            "텍스트 마이닝", "Text Mining", "언어 모델", "Language Model",
            "기계번역", "Machine Translation", "문장 분석", "Sentiment Analysis",
            "정보 추출", "Information Extraction", "질의응답", "Question Answering",
            "대화 시스템", "Dialogue System", "요약", "Summarization",
            
            # 추가 키워드
            "언어학", "Linguistics", "음성인식", "Speech Recognition", "음성합성", "Speech Synthesis",
            "음성처리", "Speech Processing", "음성분석", "Speech Analysis",
            "텍스트분석", "Text Analysis", "텍스트분류", "Text Classification",
            "개체명인식", "Named Entity Recognition", "NER", "품사태깅", "POS Tagging",
            "구문분석", "Parsing", "의존구문분석", "Dependency Parsing",
            "문장생성", "Text Generation", "번역", "Translation",
            "감정분석", "Emotion Analysis", "의견마이닝", "Opinion Mining",
            "토픽모델링", "Topic Modeling", "키워드추출", "Keyword Extraction",
            "문서분류", "Document Classification", "문서요약", "Document Summarization",
            "대화관리", "Dialogue Management", "챗봇", "Chatbot", "대화AI", "Conversational AI",
            "언어이해", "Language Understanding", "언어생성", "Language Generation",
            "프롬프트엔지니어링", "Prompt Engineering", "프롬프트", "Prompt",
            "트랜스포머", "Transformer", "BERT", "GPT", "LLM", "Large Language Model",
            "언어모델", "Language Model", "사전학습", "Pre-training", "파인튜닝", "Fine-tuning"
        ],
        "Computer Vision": [
            # 기본 키워드
            "컴퓨터 비전", "Computer Vision", "이미지 처리", "Image Processing",
            "객체 검출", "Object Detection", "이미지 분할", "Image Segmentation",
            "얼굴 인식", "Face Recognition", "영상 처리", "Video Processing",
            "3D 비전", "3D Vision", "스테레오 비전", "Stereo Vision",
            "시각적 추적", "Visual Tracking", "시각적 SLAM", "Visual SLAM",
            
            # 추가 키워드
            "이미지분류", "Image Classification", "이미지인식", "Image Recognition",
            "이미지생성", "Image Generation", "이미지복원", "Image Restoration",
            "이미지증강", "Image Augmentation", "이미지압축", "Image Compression",
            "영상분석", "Video Analysis", "영상인식", "Video Recognition",
            "영상생성", "Video Generation", "영상추적", "Video Tracking",
            "객체추적", "Object Tracking", "객체인식", "Object Recognition",
            "얼굴검출", "Face Detection", "얼굴분석", "Face Analysis",
            "얼굴생성", "Face Generation", "얼굴조작", "Face Manipulation",
            "포즈추정", "Pose Estimation", "자세추정", "Posture Estimation",
            "제스처인식", "Gesture Recognition", "행동인식", "Action Recognition",
            "활동인식", "Activity Recognition", "행동분석", "Behavior Analysis",
            "3D재구성", "3D Reconstruction", "3D모델링", "3D Modeling",
            "깊이추정", "Depth Estimation", "깊이감지", "Depth Sensing",
            "광학흐름", "Optical Flow", "모션추정", "Motion Estimation",
            "시각적주석", "Visual Annotation", "시각적질의", "Visual Query",
            "시각적검색", "Visual Search", "시각적추천", "Visual Recommendation",
            "시각적질문응답", "Visual Question Answering", "VQA",
            "이미지캡셔닝", "Image Captioning", "이미지설명", "Image Description",
            "시각적추론", "Visual Reasoning", "시각적추론", "Visual Inference",
            "CNN", "Convolutional Neural Network", "컨볼루션", "Convolution",
            "풀링", "Pooling", "특징추출", "Feature Extraction", "특징매칭", "Feature Matching"
        ],
        "Multimodal": [
            # 기본 키워드
            "멀티모달", "Multimodal", "멀티모달 학습", "Multimodal Learning",
            "시각-언어", "Vision-Language", "오디오-비전", "Audio-Vision",
            "텍스트-이미지", "Text-Image", "크로스모달", "Cross-modal",
            "멀티미디어", "Multimedia", "시각-언어 모델", "Vision-Language Model",
            
            # 추가 키워드
            "멀티모달AI", "Multimodal AI", "멀티모달퓨전", "Multimodal Fusion",
            "멀티모달정렬", "Multimodal Alignment", "멀티모달변환", "Multimodal Translation",
            "멀티모달생성", "Multimodal Generation", "멀티모달추론", "Multimodal Reasoning",
            "시각언어", "Visual Language", "시각언어모델", "Visual Language Model",
            "오디오비전", "Audio Vision", "오디오비전학습", "Audio-Visual Learning",
            "텍스트이미지", "Text Image", "텍스트이미지생성", "Text-to-Image Generation",
            "이미지텍스트", "Image Text", "이미지텍스트생성", "Image-to-Text Generation",
            "크로스모달검색", "Cross-modal Search", "크로스모달매칭", "Cross-modal Matching",
            "크로스모달변환", "Cross-modal Translation", "크로스모달생성", "Cross-modal Generation",
            "멀티미디어분석", "Multimedia Analysis", "멀티미디어검색", "Multimedia Search",
            "멀티미디어생성", "Multimedia Generation", "멀티미디어퓨전", "Multimedia Fusion",
            "시각적질문응답", "Visual Question Answering", "VQA", "시각적추론", "Visual Reasoning",
            "이미지캡셔닝", "Image Captioning", "이미지설명", "Image Description",
            "텍스트이미지검색", "Text-to-Image Search", "이미지텍스트검색", "Image-to-Text Search",
            "멀티모달임베딩", "Multimodal Embedding", "멀티모달표현", "Multimodal Representation",
            "멀티모달특징", "Multimodal Features", "멀티모달특징추출", "Multimodal Feature Extraction",
            "시각언어사전학습", "Visual Language Pre-training", "시각언어파인튜닝", "Visual Language Fine-tuning",
            "CLIP", "DALL-E", "Stable Diffusion", "Midjourney", "시각언어모델", "Vision-Language Model"
        ],
        "Machine Learning": [
            # 기본 키워드
            "기계학습", "Machine Learning", "딥러닝", "Deep Learning",
            "신경망", "Neural Network", "강화학습", "Reinforcement Learning",
            "지도학습", "Supervised Learning", "비지도학습", "Unsupervised Learning",
            "전이학습", "Transfer Learning", "메타학습", "Meta Learning",
            "적대적 학습", "Adversarial Learning", "앙상블", "Ensemble",
            "최적화", "Optimization", "딥러닝 최적화", "Deep Learning Optimization",
            
            # 추가 키워드
            "ML", "AI", "인공지능", "Artificial Intelligence", "머신러닝", "Machine Learning",
            "딥러닝", "Deep Learning", "신경망", "Neural Network", "인공신경망", "Artificial Neural Network",
            "CNN", "Convolutional Neural Network", "RNN", "Recurrent Neural Network",
            "LSTM", "Long Short-Term Memory", "GRU", "Gated Recurrent Unit",
            "트랜스포머", "Transformer", "어텐션", "Attention", "셀프어텐션", "Self-Attention",
            "강화학습", "Reinforcement Learning", "RL", "Q러닝", "Q-Learning",
            "정책그라디언트", "Policy Gradient", "액터크리틱", "Actor-Critic",
            "지도학습", "Supervised Learning", "비지도학습", "Unsupervised Learning",
            "준지도학습", "Semi-supervised Learning", "자기지도학습", "Self-supervised Learning",
            "전이학습", "Transfer Learning", "도메인적응", "Domain Adaptation",
            "메타학습", "Meta Learning", "Few-shot Learning", "원샷러닝", "One-shot Learning",
            "적대적학습", "Adversarial Learning", "GAN", "Generative Adversarial Network",
            "생성모델", "Generative Model", "VAE", "Variational Autoencoder",
            "앙상블", "Ensemble", "배깅", "Bagging", "부스팅", "Boosting",
            "랜덤포레스트", "Random Forest", "XGBoost", "LightGBM",
            "서포트벡터머신", "Support Vector Machine", "SVM", "결정트리", "Decision Tree",
            "로지스틱회귀", "Logistic Regression", "선형회귀", "Linear Regression",
            "클러스터링", "Clustering", "K-means", "K-means Clustering",
            "차원축소", "Dimensionality Reduction", "PCA", "Principal Component Analysis",
            "특징선택", "Feature Selection", "특징추출", "Feature Extraction",
            "하이퍼파라미터튜닝", "Hyperparameter Tuning", "그리드서치", "Grid Search",
            "베이지안최적화", "Bayesian Optimization", "랜덤서치", "Random Search",
            "교차검증", "Cross Validation", "K-fold", "K-fold Cross Validation",
            "과적합", "Overfitting", "과소적합", "Underfitting", "정규화", "Regularization",
            "드롭아웃", "Dropout", "배치정규화", "Batch Normalization",
            "그라디언트디센트", "Gradient Descent", "확률적그라디언트디센트", "Stochastic Gradient Descent",
            "Adam", "Adam Optimizer", "RMSprop", "Momentum", "모멘텀",
            "학습률", "Learning Rate", "배치크기", "Batch Size", "에포크", "Epoch",
            "손실함수", "Loss Function", "비용함수", "Cost Function",
            "정확도", "Accuracy", "정밀도", "Precision", "재현율", "Recall", "F1점수", "F1 Score",
            "ROC", "ROC Curve", "AUC", "Area Under Curve",
            "데이터마이닝", "Data Mining", "패턴인식", "Pattern Recognition",
            "통계학습", "Statistical Learning", "확률모델", "Probabilistic Model",
            "베이지안", "Bayesian", "베이지안네트워크", "Bayesian Network",
            "은닉마르코프모델", "Hidden Markov Model", "HMM", "가우시안믹스처모델", "Gaussian Mixture Model"
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
            
            # 연구 분야를 단어 단위로 분리
            area_words = set(re.findall(r'\b\w+\b', area_lower))
            
            for category, keywords in cls.STANDARD_CATEGORIES.items():
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    keyword_words = set(re.findall(r'\b\w+\b', keyword_lower))
                    
                    # 정확한 매칭
                    if area_lower == keyword_lower:
                        category_scores[category] += 1.0
                        break
                    
                    # 키워드가 연구 분야에 완전히 포함
                    elif keyword_lower in area_lower:
                        category_scores[category] += 0.9
                        break
                    
                    # 연구 분야가 키워드에 완전히 포함
                    elif area_lower in keyword_lower:
                        category_scores[category] += 0.8
                        break
                    
                    # 단어 단위 매칭 (공통 단어가 있으면)
                    elif area_words & keyword_words:
                        common_words = area_words & keyword_words
                        match_ratio = len(common_words) / max(len(area_words), len(keyword_words))
                        category_scores[category] += match_ratio * 0.7
                        break
        
        # 점수 정규화 (0-1 범위)
        max_score = max(category_scores.values()) if category_scores.values() else 1
        if max_score > 0:
            for category in category_scores:
                category_scores[category] = min(category_scores[category] / max_score, 1.0)
        
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
        
        # 카테고리 매핑 (확장)
        category_mapping = {
            # Machine Learning 관련
            "machine learning / deep learning (ml/dl)": "Machine Learning",
            "machine learning / deep learning": "Machine Learning",
            "machine learning / deep learning (ml/dl)": "Machine Learning",
            "ml/dl": "Machine Learning",
            "machine learning": "Machine Learning",
            "ml": "Machine Learning",
            "딥러닝": "Machine Learning",
            "deep learning": "Machine Learning",
            "기계학습": "Machine Learning",
            "기계학습(딥러닝)": "Machine Learning",
            "기계학습 기반": "Machine Learning",
            "ai": "Machine Learning",
            "인공지능": "Machine Learning",
            
            # Computer Vision 관련
            "computer vision (cv)": "Computer Vision",
            "computer vision": "Computer Vision",
            "cv": "Computer Vision",
            "컴퓨터 비전": "Computer Vision",
            "이미지 처리": "Computer Vision",
            "image processing": "Computer Vision",
            "영상처리": "Computer Vision",
            "video processing": "Computer Vision",
            
            # NLP 관련
            "natural language processing (nlp)": "NLP",
            "natural language processing": "NLP",
            "nlp": "NLP",
            "자연어처리": "NLP",
            "자연어 처리": "NLP",
            "음성처리": "NLP",
            "speech processing": "NLP",
            "텍스트분석": "NLP",
            "text analysis": "NLP",
            
            # Multimodal 관련
            "multimodal": "Multimodal",
            "멀티모달": "Multimodal",
            "시각-언어": "Multimodal",
            "vision-language": "Multimodal",
            "텍스트-이미지": "Multimodal",
            "text-image": "Multimodal",
            "크로스모달": "Multimodal",
            "cross-modal": "Multimodal"
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