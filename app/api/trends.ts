// 트렌드 분석 API 클라이언트
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'https://cvpilot-670621051738.asia-northeast3.run.app';

export interface TrendAnalysisRequest {
  field: string;
  keywords: string[];
  limit?: number;
  similarity_threshold?: number;
}

export interface TrendAnalysisResponse {
  id: string;
  field: string;
  keywords: string[];
  top_papers: Array<{
    id: string;
    title: string;
    abstract: string;
    authors: string;
    conference: string;
    year: number;
    field: string;
    url?: string;
    similarity_score?: number;
  }>;
  wordcloud_data: Record<string, number>;
  trend_summary: string;
  created_at: string;
}

export interface FieldStatistics {
  total_papers: number;
  year_distribution: Record<string, number>;
  conference_distribution: Record<string, number>;
}

export interface PopularKeywords {
  keywords: Record<string, number>;
}

// 논문 트렌드 API 호출
export async function getPaperTrend(interest: string, detailedInterests: string[] = [], limit: number = 10) {
  const params = new URLSearchParams({
    interest: interest,
    limit: limit.toString()
  });
  
  // 세부 분야가 있으면 추가
  if (detailedInterests.length > 0) {
    params.append('detailed_interests', detailedInterests.join(','));
  }
  
  const res = await fetch(`${BACKEND_URL}/api/v1/trends/paper-trend?${params}`, {
    method: "GET",
  });
  
  if (!res.ok) {
    throw new Error(`논문 트렌드 조회 실패: ${res.status}`);
  }
  
  return res.json();
}

// 트렌드 분석 수행
export async function analyzeTrends(request: TrendAnalysisRequest): Promise<TrendAnalysisResponse> {
  const response = await fetch(`${BACKEND_URL}/api/v1/trends/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '트렌드 분석 중 오류가 발생했습니다.');
  }

  return response.json();
}

// 사용 가능한 분야 목록 조회
export async function getAvailableFields(): Promise<string[]> {
  const response = await fetch(`${BACKEND_URL}/api/v1/trends/fields`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '분야 목록 조회 중 오류가 발생했습니다.');
  }

  return response.json();
}

// 특정 분야의 통계 정보 조회
export async function getFieldStatistics(field: string): Promise<FieldStatistics> {
  const response = await fetch(`${BACKEND_URL}/api/v1/trends/fields/${encodeURIComponent(field)}/statistics`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '분야 통계 조회 중 오류가 발생했습니다.');
  }

  return response.json();
}

// 특정 분야의 인기 키워드 조회
export async function getPopularKeywords(field: string, limit: number = 20): Promise<PopularKeywords> {
  const response = await fetch(
    `${BACKEND_URL}/api/v1/trends/fields/${encodeURIComponent(field)}/keywords?limit=${limit}`
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '인기 키워드 조회 중 오류가 발생했습니다.');
  }

  return response.json();
} 