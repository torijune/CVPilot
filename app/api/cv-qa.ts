// CV QA API 클라이언트
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export interface CVUploadResponse {
  success: boolean;
  analysis_id: string;
  message: string;
}

export interface QASessionRequest {
  analysis_id: string;
  mode: 'interview' | 'practice';
}

export interface QASessionResponse {
  success: boolean;
  session_id: string;
  mode: 'interview' | 'practice';
  interview_questions?: string[];
  message: string;
}

export interface QAMessage {
  message_id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  feedback?: string;  // interview 모드에서 피드백
  follow_up_question?: string;  // interview 모드에서 꼬리 질문
}

export interface QAMessageRequest {
  message: string;
}

export interface QAMessageResponse {
  success: boolean;
  message_id: string;
  content: string;
  role?: string;
  timestamp?: string;
  feedback?: string;
  follow_up_question?: string;
}

export interface InterviewQuestionsResponse {
  success: boolean;
  questions: string[];
  message: string;
}

export interface QASessionListResponse {
  success: boolean;
  sessions: any[];
  total: number;
}

// CV 파일 업로드 및 분석
export const uploadCV = async (file: File, apiKey?: string): Promise<CVUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const headers: HeadersInit = {};
  if (apiKey) {
    headers["X-API-Key"] = apiKey;
  }

  const response = await fetch(`${BACKEND_URL}/api/v1/cv-qa/upload`, {
    method: 'POST',
    headers,
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`CV 업로드 실패: ${response.status}`);
  }

  return response.json();
};

// QA 세션 생성
export const createQASession = async (request: QASessionRequest, apiKey?: string): Promise<QASessionResponse> => {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (apiKey) {
    headers["X-API-Key"] = apiKey;
  }

  const response = await fetch(`${BACKEND_URL}/api/v1/cv-qa/sessions`, {
    method: 'POST',
    headers,
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`QA 세션 생성 실패: ${response.status}`);
  }

  return response.json();
};

// 메시지 전송
export const sendMessage = async (sessionId: string, request: QAMessageRequest): Promise<QAMessageResponse> => {
  const response = await fetch(`${BACKEND_URL}/api/v1/cv-qa/sessions/${sessionId}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`메시지 전송 실패: ${response.status}`);
  }

  return response.json();
};

// 새로운 면접 질문 생성 (A 기능용)
export const getNewInterviewQuestions = async (sessionId: string): Promise<InterviewQuestionsResponse> => {
  const response = await fetch(`${BACKEND_URL}/api/v1/cv-qa/sessions/${sessionId}/new-questions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ request_new: true }),
  });

  if (!response.ok) {
    throw new Error(`새로운 면접 질문 생성 실패: ${response.status}`);
  }

  return response.json();
};

// 선택된 질문을 AI가 물어보기
export const askSelectedQuestion = async (sessionId: string, question: string): Promise<QAMessageResponse> => {
  const response = await fetch(`${BACKEND_URL}/api/v1/cv-qa/sessions/${sessionId}/ask-question`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error(`질문 전송 실패: ${response.status}`);
  }

  return response.json();
};

// 세션 메시지 목록 조회
export const getSessionMessages = async (sessionId: string): Promise<QAMessage[]> => {
  const response = await fetch(`${BACKEND_URL}/api/v1/cv-qa/sessions/${sessionId}/messages`, {
    method: 'GET',
  });

  if (!response.ok) {
    throw new Error(`메시지 목록 조회 실패: ${response.status}`);
  }

  const messages = await response.json();
  return messages.map((msg: any) => ({
    message_id: msg.message_id,
    role: msg.role,
    content: msg.content,
    timestamp: msg.timestamp,
    feedback: msg.feedback,
    follow_up_question: msg.follow_up_question,
  }));
};

// QA 세션 목록 조회
export const getQASessions = async (limit: number = 10, offset: number = 0): Promise<QASessionListResponse> => {
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString()
  });

  const response = await fetch(`${BACKEND_URL}/api/v1/cv-qa/sessions?${params}`, {
    method: 'GET',
  });

  if (!response.ok) {
    throw new Error(`QA 세션 목록 조회 실패: ${response.status}`);
  }

  return response.json();
};

// QA 세션 삭제
export const deleteQASession = async (sessionId: string): Promise<{ success: boolean; message: string }> => {
  const response = await fetch(`${BACKEND_URL}/api/v1/cv-qa/sessions/${sessionId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error(`QA 세션 삭제 실패: ${response.status}`);
  }

  return response.json();
}; 