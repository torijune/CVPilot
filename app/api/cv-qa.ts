// CV QA API 클라이언트
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export interface QAMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface QASession {
  id: string;
  cv_analysis_id: string;
  messages: QAMessage[];
  created_at: string;
}

export interface QASessionRequest {
  cv_analysis_id: string;
}

export interface QAMessageRequest {
  session_id: string;
  message: string;
}

// QA 세션 생성
export async function createQASession(cvAnalysisId: string): Promise<QASession> {
  const response = await fetch(`${BACKEND_URL}/api/v1/cv-qa/session`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      cv_analysis_id: cvAnalysisId
    }),
  });
  
  if (!response.ok) {
    throw new Error(`QA 세션 생성 실패: ${response.status}`);
  }
  
  return response.json();
}

// QA 세션 조회
export async function getQASession(sessionId: string): Promise<QASession> {
  const response = await fetch(`${BACKEND_URL}/api/v1/cv-qa/session/${sessionId}`, {
    method: "GET",
  });
  
  if (!response.ok) {
    throw new Error(`QA 세션 조회 실패: ${response.status}`);
  }
  
  return response.json();
}

// 메시지 전송
export async function sendQAMessage(sessionId: string, message: string): Promise<QAMessage> {
  const response = await fetch(`${BACKEND_URL}/api/v1/cv-qa/session/${sessionId}/message`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: message
    }),
  });
  
  if (!response.ok) {
    throw new Error(`메시지 전송 실패: ${response.status}`);
  }
  
  return response.json();
}

// QA 세션 목록 조회
export async function getQASessionList(limit: number = 10, offset: number = 0): Promise<QASession[]> {
  const response = await fetch(`${BACKEND_URL}/api/v1/cv-qa/sessions?limit=${limit}&offset=${offset}`, {
    method: "GET",
  });
  
  if (!response.ok) {
    throw new Error(`QA 세션 목록 조회 실패: ${response.status}`);
  }
  
  return response.json();
} 