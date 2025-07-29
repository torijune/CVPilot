// CV 피드백 API 클라이언트
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export interface CVFeedbackRequest {
  cv_analysis_id: string;
}

export interface CVFeedbackResponse {
  id: string;
  cv_analysis_id: string;
  improvement_projects: Array<{
    title: string;
    description: string;
    technologies: string[];
    duration: string;
    difficulty: string;
    learning_outcomes: string[];
  }>;
  skill_recommendations: string[];
  career_path_suggestions: string[];
  created_at: string;
}

// CV 피드백 생성
export async function generateCVFeedback(cvAnalysisId: string): Promise<CVFeedbackResponse> {
  const response = await fetch(`${BACKEND_URL}/api/v1/cv-feedback/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      cv_analysis_id: cvAnalysisId
    }),
  });
  
  if (!response.ok) {
    throw new Error(`CV 피드백 생성 실패: ${response.status}`);
  }
  
  return response.json();
}

// CV 피드백 조회
export async function getCVFeedback(feedbackId: string): Promise<CVFeedbackResponse> {
  const response = await fetch(`${BACKEND_URL}/api/v1/cv-feedback/${feedbackId}`, {
    method: "GET",
  });
  
  if (!response.ok) {
    throw new Error(`CV 피드백 조회 실패: ${response.status}`);
  }
  
  return response.json();
}

// CV 피드백 목록 조회
export async function getCVFeedbackList(limit: number = 10, offset: number = 0): Promise<CVFeedbackResponse[]> {
  const response = await fetch(`${BACKEND_URL}/api/v1/cv-feedback/list?limit=${limit}&offset=${offset}`, {
    method: "GET",
  });
  
  if (!response.ok) {
    throw new Error(`CV 피드백 목록 조회 실패: ${response.status}`);
  }
  
  return response.json();
} 