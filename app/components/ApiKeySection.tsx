import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  Stack,
  CircularProgress,
  Box,
  Chip,
} from '@mui/material';
import {
  Key as KeyIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  CheckCircle as CheckCircleIcon,
  Edit as EditIcon,
  Cancel as CancelIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { useApiKey } from '../hooks/useApiKey';
import { useRouter } from 'next/router';

interface ApiKeySectionProps {
  title?: string;
  description?: string;
  functionName?: string; // "CV 분석", "트렌드 분석" 등
}

const ApiKeySection: React.FC<ApiKeySectionProps> = ({ 
  title = "OpenAI API Key",
  description = "AI 기능을 사용하려면 먼저 OpenAI API Key를 설정해주세요.",
  functionName = "이 기능"
}) => {
  const { apiKey, saveApiKey, clearApiKey, hasApiKey } = useApiKey();
  const router = useRouter();
  const [tempApiKey, setTempApiKey] = useState("");
  const [showApiKey, setShowApiKey] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [validationError, setValidationError] = useState("");
  const [isEditing, setIsEditing] = useState(false);

  // 컴포넌트 마운트 시 현재 API Key를 temp 상태에 설정
  useEffect(() => {
    if (apiKey && !tempApiKey) {
      setTempApiKey(apiKey);
    }
  }, [apiKey, tempApiKey]);

  // API Key가 없으면 자동으로 편집 모드
  useEffect(() => {
    if (!hasApiKey()) {
      setIsEditing(true);
    }
  }, [hasApiKey]);

  // API Key 유효성 검증
  const validateApiKey = async (key: string): Promise<boolean> => {
    if (!key.trim()) return false;
    
    try {
      const response = await fetch('https://api.openai.com/v1/models', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${key}`,
          'Content-Type': 'application/json'
        }
      });
      return response.ok;
    } catch (error) {
      return false;
    }
  };

  // API Key 저장 핸들러
  const handleApiKeySave = async () => {
    if (!tempApiKey.trim()) {
      setValidationError('API Key를 입력해주세요.');
      return;
    }

    setIsValidating(true);
    setValidationError('');

    const isValid = await validateApiKey(tempApiKey);
    
    if (isValid) {
      saveApiKey(tempApiKey);
      setValidationError('');
      setIsEditing(false);
    } else {
      setValidationError('유효하지 않은 API Key입니다.');
    }
    
    setIsValidating(false);
  };

  // 편집 시작
  const handleStartEdit = () => {
    setTempApiKey(apiKey);
    setIsEditing(true);
    setValidationError('');
  };

  // 편집 취소
  const handleCancelEdit = () => {
    setTempApiKey(apiKey);
    setIsEditing(false);
    setValidationError('');
    setShowApiKey(false);
  };

  // API Key 삭제
  const handleDeleteApiKey = () => {
    clearApiKey();
    setTempApiKey('');
    setIsEditing(true);
    setValidationError('');
    setShowApiKey(false);
  };

  // API Key 마스킹 표시
  const getMaskedApiKey = (key: string) => {
    if (key.length <= 8) return key;
    return `${key.substring(0, 7)}${'*'.repeat(key.length - 11)}${key.substring(key.length - 4)}`;
  };

  return (
    <Paper elevation={3} sx={{ p: 2.5 }}>
      <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
        <KeyIcon sx={{ 
          mr: 1, 
          verticalAlign: 'middle', 
          color: hasApiKey() ? 'success.main' : 'warning.main' 
        }} />
        {title}
      </Typography>

      {!hasApiKey() && (
        <Stack spacing={2} sx={{ mb: 2 }}>
          <Alert 
            severity="warning" 
            sx={{ 
              background: 'linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%)',
              border: '1px solid #F59E0B',
              '& .MuiAlert-icon': {
                color: '#D97706'
              }
            }}
          >
            <Typography variant="body2">
              <strong>⚠️ API Key가 필요합니다!</strong><br />
              {functionName}을(를) 사용하려면 {description}
            </Typography>
          </Alert>
          
          <Alert 
            severity="info" 
            sx={{ 
              background: 'linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%)',
              border: '1px solid #3B82F6',
              '& .MuiAlert-icon': {
                color: '#1D4ED8'
              }
            }}
          >
            <Typography variant="body2">
              <strong>🤔 API Key 발급 방법이 궁금하다면?</strong><br />
              <Button
                variant="text"
                size="small"
                onClick={() => router.push('/api-key-guide')}
                sx={{
                  color: '#3B82F6',
                  textDecoration: 'underline',
                  p: 0,
                  minWidth: 'auto',
                  '&:hover': {
                    backgroundColor: 'transparent',
                    textDecoration: 'underline'
                  }
                }}
              >
                자세한 발급 가이드 보기 →
              </Button>
            </Typography>
          </Alert>
        </Stack>
      )}

      <Stack spacing={2}>
        {/* API Key가 있고 편집 모드가 아닐 때 - 표시 모드 */}
        {hasApiKey() && !isEditing && (
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Chip
                label={getMaskedApiKey(apiKey)}
                color="success"
                variant="outlined"
                sx={{ 
                  fontFamily: 'monospace',
                  fontSize: '0.875rem',
                  flex: 1,
                  maxWidth: 'fit-content'
                }}
              />
            </Box>
            <Stack direction="row" spacing={1}>
              <Button
                variant="outlined"
                size="small"
                startIcon={<EditIcon />}
                onClick={handleStartEdit}
                sx={{ flex: 1 }}
              >
                변경
              </Button>
              <Button
                variant="outlined"
                size="small"
                color="error"
                startIcon={<DeleteIcon />}
                onClick={handleDeleteApiKey}
                sx={{ flex: 1 }}
              >
                삭제
              </Button>
            </Stack>
          </Box>
        )}

        {/* 편집 모드 */}
        {isEditing && (
          <>
            <TextField
              fullWidth
              size="small"
              placeholder="sk-..."
              type={showApiKey ? 'text' : 'password'}
              value={tempApiKey}
              onChange={(e) => setTempApiKey(e.target.value)}
              InputProps={{
                startAdornment: (
                  <KeyIcon sx={{ color: 'text.secondary', mr: 1 }} />
                ),
                endAdornment: (
                  <Button
                    size="small"
                    onClick={() => setShowApiKey(!showApiKey)}
                    sx={{ minWidth: 'auto', p: 0.5 }}
                  >
                    {showApiKey ? <VisibilityOffIcon fontSize="small" /> : <VisibilityIcon fontSize="small" />}
                  </Button>
                ),
              }}
            />

            {validationError && (
              <Alert severity="error" sx={{ py: 0.5 }}>
                <Typography variant="caption">
                  {validationError}
                </Typography>
              </Alert>
            )}

            <Stack direction="row" spacing={1}>
              <Button
                fullWidth
                variant="contained"
                onClick={handleApiKeySave}
                disabled={isValidating || !tempApiKey.trim()}
                startIcon={isValidating ? <CircularProgress size={16} /> : <CheckCircleIcon />}
              >
                {isValidating ? '검증 중...' : hasApiKey() ? '업데이트' : '저장'}
              </Button>
              
              {hasApiKey() && (
                <Button
                  variant="outlined"
                  onClick={handleCancelEdit}
                  startIcon={<CancelIcon />}
                  sx={{ minWidth: '100px' }}
                >
                  취소
                </Button>
              )}
            </Stack>
          </>
        )}
      </Stack>

      {hasApiKey() && !isEditing && (
        <Alert 
          severity="success" 
          sx={{ 
            mt: 2,
            background: 'linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%)',
            border: '1px solid #10B981',
            '& .MuiAlert-icon': {
              color: '#059669'
            }
          }}
        >
          <Typography variant="body2">
            <strong>✅ API Key 설정됨</strong> - 모든 AI 기능을 사용할 수 있습니다.
          </Typography>
        </Alert>
      )}
    </Paper>
  );
};

export default ApiKeySection; 