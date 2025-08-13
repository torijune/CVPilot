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
  reviewer_feedback: string;
  recommendations: string[];
  created_at: string;
}



// 방법론 비교 수행
export async function compareMethods(request: MethodComparisonRequest, apiKey?: string): Promise<MethodComparisonResponse> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (apiKey) {
    headers["X-API-Key"] = apiKey;
  }

  const response = await fetch(`${BACKEND_URL}/api/v1/comparison/compare`, {
    method: 'POST',
    headers,
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

 