const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiConfig = {
  baseURL: API_BASE_URL,
  endpoints: {
    cvAnalysis: `${API_BASE_URL}/api/v1/cv`,
    trends: `${API_BASE_URL}/api/v1/trends`,
    comparison: `${API_BASE_URL}/api/v1/comparison`,
    podcast: `${API_BASE_URL}/api/v1/podcast`,
    labAnalysis: `${API_BASE_URL}/api/v1/lab-analysis`,
    cvQA: `${API_BASE_URL}/api/v1/cv-qa`,
    labs: `${API_BASE_URL}/api/v1/labs`,
  }
};

export default apiConfig; 