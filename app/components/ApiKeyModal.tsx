import React, { useState } from 'react';
import { useRouter } from 'next/router';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  IconButton,
  InputAdornment
} from '@mui/material';
import { Visibility, VisibilityOff, Key } from '@mui/icons-material';

interface ApiKeyModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (apiKey: string) => void;
  currentApiKey?: string;
  redirectToHome?: boolean; // 홈페이지로 리다이렉트할지 여부
}

const ApiKeyModal: React.FC<ApiKeyModalProps> = ({
  open,
  onClose,
  onSave,
  currentApiKey,
  redirectToHome = false
}) => {
  const router = useRouter();
  const [apiKey, setApiKey] = useState(currentApiKey || '');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isValidating, setIsValidating] = useState(false);

  const handleSave = async () => {
    if (!apiKey.trim()) {
      setError('API Key를 입력해주세요.');
      return;
    }

    setIsValidating(true);
    setError('');

    try {
      // API Key 유효성 검증 (간단한 테스트)
      const response = await fetch('https://api.openai.com/v1/models', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        onSave(apiKey);
        onClose();
      } else {
        const errorData = await response.json().catch(() => ({}));
        if (response.status === 401) {
          setError('API Key가 유효하지 않습니다. 올바른 OpenAI API Key를 입력해주세요.');
        } else if (response.status === 429) {
          setError('API 사용량이 초과되었습니다. 잠시 후 다시 시도해주세요.');
        } else {
          setError(`API Key 검증 실패: ${errorData.error?.message || '알 수 없는 오류'}`);
        }
      }
    } catch (err) {
      setError('API Key 검증 중 오류가 발생했습니다. 네트워크 연결을 확인해주세요.');
    } finally {
      setIsValidating(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <Key color="primary" />
          <Typography variant="h6">OpenAI API Key 설정</Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          AI 기능을 사용하기 위해 OpenAI API Key가 필요합니다.
          <br />
          <strong>서버 API Key는 제공되지 않으므로 반드시 직접 입력해주세요.</strong>
        </Typography>

        <Alert severity="warning" sx={{ 
          mb: 2,
          background: 'linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%)',
          border: '1px solid #F59E0B',
          '& .MuiAlert-icon': {
            color: '#D97706'
          }
        }}>
          <Typography variant="body2">
            <strong>⚠️ API Key가 필요합니다!</strong>
            <br />
            이 기능을 사용하려면 OpenAI API Key를 먼저 설정해주세요.
          </Typography>
        </Alert>

        <TextField
          fullWidth
          label="OpenAI API Key"
          type={showPassword ? 'text' : 'password'}
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          placeholder="sk-..."
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={() => setShowPassword(!showPassword)}
                  edge="end"
                >
                  {showPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ),
          }}
          sx={{ mb: 2 }}
        />

        <Alert severity="info" sx={{ 
          mb: 2,
          background: 'linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%)',
          border: '1px solid #3B82F6',
          '& .MuiAlert-icon': {
            color: '#2563EB'
          }
        }}>
          <Typography variant="body2">
            • API Key는 로컬에 안전하게 저장됩니다.<br/>
            • 서버로 전송되지 않으며, 브라우저에서만 사용됩니다.<br/>
            • <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" style={{ color: '#2563EB', fontWeight: 600 }}>
              OpenAI API Key 발급받기
            </a>
          </Typography>
        </Alert>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
      </DialogContent>

      <DialogActions>
        <Button 
          onClick={() => {
            if (redirectToHome) {
              router.push('/');
            } else {
              onClose();
            }
          }} 
          disabled={isValidating}
          sx={{
            color: '#6B7280',
            borderColor: '#D1D5DB',
            '&:hover': {
              borderColor: '#9CA3AF',
              backgroundColor: '#F9FAFB'
            }
          }}
        >
          취소
        </Button>
        <Button
          onClick={handleSave}
          variant="contained"
          disabled={isValidating || !apiKey.trim()}
          sx={{
            background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
              transform: 'translateY(-1px)',
              boxShadow: '0 4px 12px rgba(16, 185, 129, 0.4)'
            },
            '&:disabled': {
              background: '#D1D5DB',
              transform: 'none',
              boxShadow: 'none'
            },
            transition: 'all 0.3s ease',
            borderRadius: 2,
            px: 3
          }}
        >
          {isValidating ? '검증 중...' : '저장'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ApiKeyModal; 