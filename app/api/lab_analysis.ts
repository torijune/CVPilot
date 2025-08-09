// 연구실 분석 API 클라이언트
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'https://cvpilot-670621051738.asia-northeast3.run.app';

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
export async function getProfessorsByField(field: string): Promise<ProfessorListResponse> {
  const response = await fetch(`${BACKEND_URL}/api/v1/lab-analysis/professors/${encodeURIComponent(field)}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  
  if (!response.ok) {
    throw new Error(`교수 목록 조회 실패: ${response.status}`);
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
