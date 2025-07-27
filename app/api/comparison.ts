// 방법론 비교 API 클라이언트
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export interface MethodComparisonRequest {
  user_idea: string;
  field: string;
  similarity_threshold?: number;
  max_similar_papers?: number;
}

export interface MethodComparisonResponse {
  id: string;
  user_idea: string;
  field: string;
  similar_papers: Array<{
    id: string;
    title: string;
    abstract: string;
    authors: string;
    conference: string;
    year: number;
    field: string;
    similarity_score: number;
    url?: string;
  }>;
  comparison_analysis: string;
  differentiation_strategy: string;
  recommendations: string[];
  created_at: string;
}

export interface FieldStatistics {
  total_papers: number;
  year_distribution: Record<string, number>;
  conference_distribution: Record<string, number>;
}

export interface ResearchTrends {
  recent_papers_count: number;
  top_keywords: Record<string, number>;
  yearly_trend: Record<string, number>;
}

// 방법론 비교 수행
export async function compareMethods(request: MethodComparisonRequest): Promise<MethodComparisonResponse> {
  const response = await fetch(`${BACKEND_URL}/api/v1/comparison/compare`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '방법론 비교 중 오류가 발생했습니다.');
  }

  return response.json();
}

// 사용 가능한 분야 목록 조회
export async function getAvailableFields(): Promise<string[]> {
  const response = await fetch(`${BACKEND_URL}/api/v1/comparison/fields`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '분야 목록 조회 중 오류가 발생했습니다.');
  }

  return response.json();
}

// 특정 분야의 통계 정보 조회
export async function getFieldStatistics(field: string): Promise<FieldStatistics> {
  const response = await fetch(`${BACKEND_URL}/api/v1/comparison/fields/${encodeURIComponent(field)}/statistics`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '분야 통계 조회 중 오류가 발생했습니다.');
  }

  return response.json();
}

// 특정 분야의 연구 트렌드 분석
export async function getResearchTrends(field: string): Promise<ResearchTrends> {
  const response = await fetch(`${BACKEND_URL}/api/v1/comparison/fields/${encodeURIComponent(field)}/trends`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '연구 트렌드 분석 중 오류가 발생했습니다.');
  }

  return response.json();
} 