// 팟캐스트 API 클라이언트
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export interface PodcastGenerationRequest {
  field: string;
  papers?: any[]
  analysis_type?: string;
}

export interface PodcastAnalysisResponse {
  id: string;
  field: string;
  papers: Array<{
    title: string;
    abstract: string;
    authors: string[];
  }>;
  analysis_text: string;
  audio_file_path: string;
  duration_seconds: number;
  created_at: string;
}

export interface PodcastListResponse {
  podcasts: PodcastAnalysisResponse[];
  total: number;
}

export interface AvailableFieldsResponse {
  fields: string[];
}

export interface ConferenceInfo {
  name: string;
  paper_count: number;
  latest_year: number;
  year_range: string;
}

export interface ConferencesResponse {
  field: string;
  conferences: ConferenceInfo[];
  total_conferences: number;
}

export interface PaperPreviewInfo {
  id: string;
  title: string;
  abstract: string;
  authors: string[];
  conference?: string;
  year?: number;
  field: string;
  url?: string;
}

export interface PaperPreviewResponse {
  paper: PaperPreviewInfo;
  field: string;
  conference: string;
  can_reselect: boolean;
  total_papers_in_conference: number;
}

// 논문 분석만 수행
export const analyzePaper = async (field: string, papers: any[]) => {
  const response = await fetch(`${BACKEND_URL}/api/v1/podcast/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      field: field,
      papers: papers
    }),
  });
  
  if (!response.ok) {
    throw new Error(`논문 분석 실패: ${response.status}`);
  }
  
  return response.json();
};

// TTS 대본 및 오디오 생성
export const generateTTS = async (analysisId: string, ttsSettings?: any) => {
  const response = await fetch(`${BACKEND_URL}/api/v1/podcast/generate-tts/${analysisId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      tts_settings: ttsSettings
    }),
  });
  
  if (!response.ok) {
    throw new Error(`TTS 생성 실패: ${response.status}`);
  }
  
  return response.json();
};

// 팟캐스트 생성 (전체 과정)
export const generatePodcast = async (field: string, papers: any[]) => {
  const response = await fetch(`${BACKEND_URL}/api/v1/podcast/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      field: field,
      papers: papers
    }),
  });
  
  if (!response.ok) {
    throw new Error(`팟캐스트 생성 실패: ${response.status}`);
  }
  
  return response.json();
};

// 팟캐스트 분석 결과 조회
export const getPodcastAnalysis = async (analysisId: string) => {
  const response = await fetch(`${BACKEND_URL}/api/v1/podcast/analysis/${analysisId}`, {
    method: "GET",
  });
  
  if (!response.ok) {
    throw new Error(`팟캐스트 분석 결과 조회 실패: ${response.status}`);
  }
  
  return response.json();
};

// 팟캐스트 목록 조회
export const getPodcastList = async (field?: string, limit: number = 10, offset: number = 0) => {
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString()
  });
  
  if (field) {
    params.append('field', field);
  }
  
  const response = await fetch(`${BACKEND_URL}/api/v1/podcast/list?${params}`, {
    method: "GET",
  });
  
  if (!response.ok) {
    throw new Error(`팟캐스트 목록 조회 실패: ${response.status}`);
  }
  
  return response.json();
};

// 사용 가능한 분야 목록 조회
export const getAvailableFields = async () => {
  const response = await fetch(`${BACKEND_URL}/api/v1/podcast/fields`, {
    method: "GET",
  });
  
  if (!response.ok) {
    throw new Error(`분야 목록 조회 실패: ${response.status}`);
  }
  
  return response.json();
};

// 팟캐스트 분석 삭제
export const deletePodcastAnalysis = async (analysisId: string) => {
  const response = await fetch(`${BACKEND_URL}/api/v1/podcast/analysis/${analysisId}`, {
    method: "DELETE",
  });
  
  if (!response.ok) {
    throw new Error(`팟캐스트 분석 삭제 실패: ${response.status}`);
  }
  
  return response.json();
};

// 분야별 학회 목록 조회
export const getConferencesByField = async (field: string): Promise<ConferencesResponse> => {
  const response = await fetch(`${BACKEND_URL}/api/v1/podcast/conferences/${encodeURIComponent(field)}`, {
    method: "GET",
  });
  
  if (!response.ok) {
    throw new Error(`학회 목록 조회 실패: ${response.status}`);
  }
  
  return response.json();
};

// 특정 분야와 학회의 랜덤 논문 미리보기
export const getPaperPreview = async (field: string, conference: string): Promise<PaperPreviewResponse> => {
  const response = await fetch(`${BACKEND_URL}/api/v1/podcast/papers/preview/${encodeURIComponent(field)}/${encodeURIComponent(conference)}`, {
    method: "GET",
  });
  
  if (!response.ok) {
    throw new Error(`논문 미리보기 조회 실패: ${response.status}`);
  }
  
  return response.json();
};

// 같은 조건으로 다른 논문 재선택
export const reselectPaper = async (field: string, conference: string, currentPaperId?: string): Promise<PaperPreviewResponse> => {
  const response = await fetch(`${BACKEND_URL}/api/v1/podcast/papers/reselect/${encodeURIComponent(field)}/${encodeURIComponent(conference)}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      current_paper_id: currentPaperId
    }),
  });
  
  if (!response.ok) {
    throw new Error(`논문 재선택 실패: ${response.status}`);
  }
  
  return response.json();
}; 