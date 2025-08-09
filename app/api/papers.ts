// 논문 분석 API 클라이언트
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'https://cvpilot-670621051738.asia-northeast3.run.app';

export interface PaperAnalysisRequest {
  paper_id: string;
  include_tts?: boolean;
  analysis_depth?: 'basic' | 'detailed' | 'comprehensive';
}

export interface PaperAnalysisResponse {
  id: string;
  paper_id: string;
  title: string;
  problem_definition: string;
  proposed_method: string;
  experimental_setup: string;
  key_results: string;
  research_significance: string;
  tts_audio_url?: string;
  created_at: string;
}

export interface Paper {
  id: string;
  title: string;
  abstract: string;
  authors: string;
  conference: string;
  year: number;
  field: string;
  url?: string;
}

// 논문 분석 수행
export async function analyzePaper(request: PaperAnalysisRequest): Promise<PaperAnalysisResponse> {
  const response = await fetch(`${BACKEND_URL}/api/v1/papers/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '논문 분석 중 오류가 발생했습니다.');
  }

  return response.json();
}

// 랜덤 논문 조회
export async function getRandomPaper(field?: string): Promise<Paper> {
  const url = field 
    ? `${BACKEND_URL}/api/v1/papers/random?field=${encodeURIComponent(field)}`
    : `${BACKEND_URL}/api/v1/papers/random`;
    
  const response = await fetch(url);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '랜덤 논문 조회 중 오류가 발생했습니다.');
  }

  return response.json();
}

// 논문 검색
export async function searchPapers(
  query: string, 
  field?: string, 
  limit: number = 10
): Promise<Paper[]> {
  const params = new URLSearchParams({
    query: query,
    limit: limit.toString()
  });
  
  if (field) {
    params.append('field', field);
  }

  const response = await fetch(`${BACKEND_URL}/api/v1/papers/search?${params}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '논문 검색 중 오류가 발생했습니다.');
  }

  return response.json();
}

// 특정 논문 조회
export async function getPaper(paperId: string): Promise<Paper> {
  const response = await fetch(`${BACKEND_URL}/api/v1/papers/${paperId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '논문 조회 중 오류가 발생했습니다.');
  }

  return response.json();
}

// 분야별 논문 조회
export async function getPapersByField(field: string, limit: number = 50): Promise<Paper[]> {
  const response = await fetch(
    `${BACKEND_URL}/api/v1/papers/field/${encodeURIComponent(field)}?limit=${limit}`
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '분야별 논문 조회 중 오류가 발생했습니다.');
  }

  return response.json();
} 