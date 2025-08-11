import { useState, useEffect, useCallback } from 'react';

const API_KEY_STORAGE_KEY = 'cvpilot_openai_api_key';

// 전역 이벤트 리스너를 위한 커스텀 이벤트
const API_KEY_CHANGED_EVENT = 'cvpilot-api-key-changed';

export const useApiKey = () => {
  const [apiKey, setApiKey] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  // 로컬 스토리지에서 API Key를 가져오는 함수
  const loadApiKey = useCallback(() => {
    const storedApiKey = localStorage.getItem(API_KEY_STORAGE_KEY);
    return storedApiKey || '';
  }, []);

  // API Key 변경 이벤트 리스너
  useEffect(() => {
    const handleApiKeyChange = () => {
      const newApiKey = loadApiKey();
      setApiKey(newApiKey);
      console.log('API Key 변경 감지:', newApiKey ? '설정됨' : '제거됨');
    };

    // 초기 로드
    const storedApiKey = loadApiKey();
    setApiKey(storedApiKey);
    setIsLoading(false);
    console.log('초기 API Key 로드:', storedApiKey ? '설정됨' : '없음');

    // 이벤트 리스너 등록
    window.addEventListener(API_KEY_CHANGED_EVENT, handleApiKeyChange);

    // 컴포넌트 언마운트 시 이벤트 리스너 제거
    return () => {
      window.removeEventListener(API_KEY_CHANGED_EVENT, handleApiKeyChange);
    };
  }, [loadApiKey]);

  const saveApiKey = useCallback((newApiKey: string) => {
    if (newApiKey) {
      localStorage.setItem(API_KEY_STORAGE_KEY, newApiKey);
    } else {
      localStorage.removeItem(API_KEY_STORAGE_KEY);
    }
    setApiKey(newApiKey);
    
    // 다른 컴포넌트들에게 API Key 변경 알림
    window.dispatchEvent(new CustomEvent(API_KEY_CHANGED_EVENT));
  }, []);

  const clearApiKey = useCallback(() => {
    localStorage.removeItem(API_KEY_STORAGE_KEY);
    setApiKey('');
    
    // 다른 컴포넌트들에게 API Key 변경 알림
    window.dispatchEvent(new CustomEvent(API_KEY_CHANGED_EVENT));
  }, []);

  const hasApiKey = useCallback(() => {
    return apiKey.length > 0;
  }, [apiKey]);

  return {
    apiKey,
    saveApiKey,
    clearApiKey,
    hasApiKey,
    isLoading
  };
}; 