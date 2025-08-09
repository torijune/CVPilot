// CV 분석 API 클라이언트
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'https://cvpilot-670621051738.asia-northeast3.run.app';

export interface CVAnalysisRequest {
  cv_text: string;
  field: string;
}

export interface CVAnalysisResponse {
  id: string;
  cv_text: string;
  skills: string[];
  experiences: any[];
  strengths: string[];
  weaknesses: string[];
  radar_chart_data: any;
  created_at: string;
}

// 파일 업로드 및 관심분야 전송
export async function uploadCVAndInterest(cvFile: File, interests: string[]) {
  const formData = new FormData();
  formData.append("cv", cvFile);
  formData.append("interests", JSON.stringify(interests));
  const res = await fetch("/api/v1/user/interest", {
    method: "POST",
    body: formData,
  });
  return res.json();
}

// CV 분석 API 호출 (텍스트 입력)
export async function analyzeCV(cvText: string, field: string = "Machine Learning / Deep Learning (ML/DL)") {
  const response = await fetch(`${BACKEND_URL}/api/v1/cv/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      cv_text: cvText,
      field: field
    }),
  });
  
  if (!response.ok) {
    throw new Error(`CV 분석 실패: ${response.status}`);
  }
  
  return response.json();
}

// CV 분석 API 호출 (파일 업로드)
export async function analyzeCVFromFile(file: File, field: string = "Machine Learning / Deep Learning (ML/DL)") {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("field", field);
  
  const response = await fetch(`${BACKEND_URL}/api/v1/cv/analyze/upload`, {
    method: "POST",
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error(`CV 파일 분석 실패: ${response.status}`);
  }
  
  return response.json();
}

// CV 분석 결과 조회
export async function getCVAnalysis(analysisId: string) {
  const response = await fetch(`${BACKEND_URL}/api/v1/cv/analysis/${analysisId}`, {
    method: "GET",
  });
  
  if (!response.ok) {
    throw new Error(`CV 분석 결과 조회 실패: ${response.status}`);
  }
  
  return response.json();
}

// 레이더 차트 데이터 조회
export async function getRadarChartData(analysisId: string) {
  const response = await fetch(`${BACKEND_URL}/api/v1/cv/radar-chart/${analysisId}`, {
    method: "GET",
  });
  
  if (!response.ok) {
    throw new Error(`레이더 차트 데이터 조회 실패: ${response.status}`);
  }
  
  return response.json();
}

// 파일에서 텍스트 추출
export async function extractTextFromFile(file: File): Promise<string> {
  // 간단한 텍스트 파일 처리 (실제로는 PDF 파싱 라이브러리 사용 필요)
  if (file.type === "text/plain") {
    return await file.text();
  }
  
  // PDF나 다른 형식의 파일은 백엔드에서 처리하도록 파일 업로드
  const formData = new FormData();
  formData.append("file", file);
  
  const res = await fetch(`${BACKEND_URL}/api/v1/cv-loader/extract-text`, {
    method: "POST",
    body: formData,
  });
  
  if (!res.ok) {
    throw new Error(`파일 텍스트 추출 실패: ${res.status}`);
  }
  
  const data = await res.json();
  return data.text;
} 