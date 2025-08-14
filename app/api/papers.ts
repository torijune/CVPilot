// 논문 분석 API 클라이언트
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

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

// 사용 가능한 분야 목록 조회
export async function getAvailableFields(): Promise<string[]> {
  try {
    console.log('API 호출 시작:', `${BACKEND_URL}/api/v1/comparison/fields`);
    
    const response = await fetch(`${BACKEND_URL}/api/v1/comparison/fields`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      // CORS 설정
      mode: 'cors',
      credentials: 'omit'
    });
    
    console.log('API 응답 상태:', response.status, response.statusText);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('API 에러 응답:', errorText);
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    console.log('API 응답 데이터:', data);
    
    // 데이터 검증
    if (!data || !Array.isArray(data.fields)) {
      console.error('잘못된 API 응답 형식:', data);
      throw new Error('잘못된 API 응답 형식');
    }
    
    return data.fields;
  } catch (error) {
    console.error('getAvailableFields 에러:', error);
    throw error;
  }
} 