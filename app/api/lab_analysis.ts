// 연구실 분석 API 클라이언트
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export interface ProfessorInfo {
  professor_name: string;
  university_name: string;
  research_areas: string[];
  publications: string[];
  category_scores: Record<string, number>;
  primary_category: string;
  url?: string;
}

export interface ProfessorListResponse {
  field: string;
  professors: ProfessorInfo[];
  total_count: number;
}

export interface LabAnalysisRequest {
  professor_name: string;
  university_name: string;
  field: string;
}

export interface LabAnalysisResult {
  id: string;
  professor_name: string;
  university_name: string;
  field: string;
  recent_publications: Array<{
    title: string;
    abstract: string;
  }>;
  analysis_summary: string;
  research_trends: string;
  key_insights: string;
  created_at: string;
}

// 분야별 교수 목록 조회
export async function getProfessorsByField(field: string, university?: string): Promise<ProfessorListResponse> {
  let url = `${BACKEND_URL}/api/v1/lab-analysis/professors?field=${encodeURIComponent(field)}`;
  
  // 학교 필터가 있는 경우 쿼리 파라미터 추가
  if (university) {
    url += `&university=${encodeURIComponent(university)}`;
  }
  
  console.log('API 호출 URL:', url);
  console.log('원본 분야명:', field);
  console.log('인코딩된 분야명:', encodeURIComponent(field));
  
  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  
  if (!response.ok) {
    console.error('API 응답 오류:', response.status, response.statusText);
    throw new Error(`교수 목록 조회 실패: ${response.status}`);
  }
  
  return response.json();
}

// 모든 대학 목록 조회
export async function getAllUniversities(): Promise<{ universities: string[]; total_count: number }> {
  const response = await fetch(`${BACKEND_URL}/api/v1/labs/universities`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  
  if (!response.ok) {
    throw new Error(`대학 목록 조회 실패: ${response.status}`);
  }
  
  return response.json();
}

// 연구실 분석 수행
export async function analyzeLab(request: LabAnalysisRequest): Promise<LabAnalysisResult> {
  const response = await fetch(`${BACKEND_URL}/api/v1/lab-analysis/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    throw new Error(`연구실 분석 실패: ${response.status}`);
  }
  
  return response.json();
}

// 분석 결과 조회
export async function getAnalysisResult(resultId: string): Promise<LabAnalysisResult> {
  const response = await fetch(`${BACKEND_URL}/api/v1/lab-analysis/result/${resultId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  
  if (!response.ok) {
    throw new Error(`분석 결과 조회 실패: ${response.status}`);
  }
  
  return response.json();
}

// 헬스체크
export async function checkLabAnalysisHealth(): Promise<{ status: string; service: string }> {
  const response = await fetch(`${BACKEND_URL}/api/v1/lab-analysis/health`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  
  if (!response.ok) {
    throw new Error(`헬스체크 실패: ${response.status}`);
  }
  
  return response.json();
}

// 사용 가능한 분야 목록 조회
export async function getAvailableFields(): Promise<string[]> {
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/lab-analysis/fields`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    
    if (!data || !Array.isArray(data.fields)) {
      throw new Error('잘못된 API 응답 형식');
    }
    
    return data.fields;
  } catch (error) {
    console.error('getAvailableFields 에러:', error);
    throw error;
  }
}
