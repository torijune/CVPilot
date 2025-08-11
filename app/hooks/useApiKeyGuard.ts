import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { useApiKey } from './useApiKey';

export const useApiKeyGuard = (redirectToHome: boolean = true) => {
  const { apiKey, isLoading } = useApiKey();
  const router = useRouter();
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);

  useEffect(() => {
    // 로딩이 완료되고 API Key가 없으면
    if (!isLoading && !apiKey) {
      if (redirectToHome) {
        // 홈페이지로 리다이렉트
        router.push('/');
      } else {
        // 모달 표시
        setShowApiKeyModal(true);
      }
    }
  }, [apiKey, isLoading, redirectToHome, router]);

  const handleApiKeySave = (newApiKey: string) => {
    // API Key가 설정되면 모달 닫기
    setShowApiKeyModal(false);
  };

  return {
    apiKey,
    isLoading,
    showApiKeyModal,
    setShowApiKeyModal,
    handleApiKeySave,
    hasApiKey: !!apiKey
  };
}; 