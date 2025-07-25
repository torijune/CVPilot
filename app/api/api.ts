// 예시: 파일 업로드 및 관심분야 전송
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

// 기타 단계별 API 함수도 여기에 추가

// 백엔드 서버 URL 설정
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// CV 분석 API 호출
export async function analyzeCV(cvText: string, interests: string[]) {
  const formData = new FormData();
  formData.append("cv_text", cvText);
  formData.append("interests", interests.join(","));
  
  const res = await fetch(`${BACKEND_URL}/api/v1/cv-analysis/cv-analysis`, {
    method: "POST",
    body: formData,
  });
  
  if (!res.ok) {
    throw new Error(`CV 분석 실패: ${res.status}`);
  }
  
  return res.json();
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
  
  const res = await fetch(`${BACKEND_URL}/api/v1/paper-trend/paper-trend?${params}`, {
    method: "GET",
  });
  
  if (!res.ok) {
    throw new Error(`논문 트렌드 조회 실패: ${res.status}`);
  }
  
  return res.json();
}

// 파일에서 텍스트 추출 (CV 파일 처리용)
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
