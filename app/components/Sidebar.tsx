import React, { useState, useRef, useEffect } from "react";
import { Box, Typography, Button, Paper, useTheme, TextField, InputAdornment, IconButton, Alert } from "@mui/material";
import { useRouter } from "next/router";
import CVUploader from "./CVUploader";
import InterestSelector from "./InterestSelector";
import { useApiKey } from "../hooks/useApiKey";
import FlightTakeoffIcon from "@mui/icons-material/FlightTakeoff";
import HomeIcon from "@mui/icons-material/Home";
import KeyIcon from "@mui/icons-material/Key";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";

type Props = {
  onAnalyze: (cvFile: File | null, interests: string[]) => void;
  loading: boolean;
  onWidthChange?: (width: number) => void;
};

const Sidebar: React.FC<Props> = ({ onAnalyze, loading, onWidthChange }) => {
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [interests, setInterests] = useState<string[]>([]);
  const [sidebarWidth, setSidebarWidth] = useState(340); // 짧은 마스킹으로 줄어든 너비
  const [isResizing, setIsResizing] = useState(false);
  const [showApiKey, setShowApiKey] = useState(false);
  const [tempApiKey, setTempApiKey] = useState("");
  const [isValidating, setIsValidating] = useState(false);
  const [validationError, setValidationError] = useState("");
  
  const resizeRef = useRef<HTMLDivElement>(null);
  const theme = useTheme();
  const router = useRouter();
  const { apiKey, saveApiKey, hasApiKey } = useApiKey();

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
      setTempApiKey("");
      setValidationError('');
    } else {
      setValidationError('유효하지 않은 API Key입니다.');
    }
    
    setIsValidating(false);
  };

  // 컴포넌트 마운트 시 현재 API Key를 temp 상태에 설정
  useEffect(() => {
    if (apiKey && !tempApiKey) {
      setTempApiKey(apiKey);
    }
  }, [apiKey, tempApiKey]);

  // 최소/최대 너비 설정 (80% 스케일에 맞춤)
  const MIN_WIDTH = 340; // 짧은 마스킹으로 줄어든 너비
  const MAX_WIDTH = 480; // 600 * 0.8 = 480

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;

      const newWidth = e.clientX;
      if (newWidth >= MIN_WIDTH && newWidth <= MAX_WIDTH) {
        setSidebarWidth(newWidth);
        onWidthChange?.(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing, onWidthChange]);

  const handleMouseDown = () => {
    setIsResizing(true);
  };

  return (
    <Box sx={{ position: 'relative', height: '100%' }}>
      {/* 사이드바 컨텐츠 */}
      <Paper
        elevation={0}
        sx={{
          width: sidebarWidth,
          height: '100%',
          borderRadius: 0,
          display: 'flex',
          flexDirection: 'column',
          transition: isResizing ? 'none' : 'width 0.2s ease',
          overflow: 'hidden',
          background: 'linear-gradient(180deg, #1F2937 0%, #374151 100%)',
          borderRight: '1px solid #E5E7EB'
        }}
      >
        <Box sx={{ 
          p: 2.5, 
          height: '100%', 
          overflow: 'auto',
          display: 'flex',
          flexDirection: 'column'
        }}>
          {/* CareerPilot 브랜드 로고 */}
          <Box sx={{ 
            mb: 4, 
            textAlign: 'center',
            pb: 3,
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              mb: 1
            }}>
              <FlightTakeoffIcon sx={{ 
                fontSize: 32, 
                color: '#3B82F6',
                mr: 1,
                filter: 'drop-shadow(0 2px 4px rgba(59, 130, 246, 0.3))'
              }} />
              <Typography 
                variant="h4" 
                sx={{ 
                  fontWeight: 800, 
                  background: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  fontSize: '1.75rem',
                  letterSpacing: '-0.025em'
                }}
              >
                CVPilot
              </Typography>
            </Box>
            <Typography 
              variant="body2" 
              sx={{ 
                color: '#9CA3AF',
                fontSize: '0.875rem',
                fontWeight: 500,
                letterSpacing: '0.025em'
              }}
            >
              AI-Powered Curriculum Vitae Advisor
            </Typography>
            
            {/* 홈페이지로 돌아가기 버튼 */}
            <Button
              variant="outlined"
              size="small"
              startIcon={<HomeIcon />}
              onClick={() => router.push('/')}
              sx={{
                mt: 2,
                borderColor: 'rgba(255, 255, 255, 0.3)',
                color: 'rgba(255, 255, 255, 0.8)',
                fontSize: '0.75rem',
                py: 0.5,
                px: 2,
                '&:hover': {
                  borderColor: 'rgba(255, 255, 255, 0.6)',
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  color: 'white'
                }
              }}
            >
              홈으로
            </Button>
          </Box>
          
          {/* API Key 설정 섹션 */}
          <Box sx={{ 
            mb: 3, 
            p: 1.5,
            borderRadius: 2,
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              mb: 2 
            }}>
              <KeyIcon sx={{ 
                color: hasApiKey() ? '#10B981' : '#F59E0B', 
                mr: 1, 
                fontSize: 20 
              }} />
              <Typography 
                variant="subtitle2" 
                sx={{ 
                  color: 'white', 
                  fontWeight: 600,
                  flex: 1
                }}
              >
                OpenAI API Key
              </Typography>
              {hasApiKey() && (
                <CheckCircleIcon sx={{ 
                  color: '#10B981', 
                  fontSize: 16 
                }} />
              )}
            </Box>

            {!hasApiKey() && (
              <Alert 
                severity="warning" 
                sx={{ 
                  mb: 2,
                  background: 'rgba(245, 158, 11, 0.1)',
                  border: '1px solid rgba(245, 158, 11, 0.3)',
                  color: '#FCD34D',
                  '& .MuiAlert-icon': {
                    color: '#F59E0B'
                  }
                }}
              >
                <Typography variant="caption" sx={{ fontSize: '0.7rem' }}>
                  AI 기능 사용을 위해 API Key가 필요합니다.
                </Typography>
              </Alert>
            )}

            {hasApiKey() && (
              <Alert 
                severity="success" 
                sx={{ 
                  mb: 2,
                  background: 'rgba(16, 185, 129, 0.1)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  color: '#A7F3D0',
                  '& .MuiAlert-icon': {
                    color: '#10B981'
                  }
                }}
              >
                <Typography variant="caption" sx={{ fontSize: '0.65rem' }}>
                  API Key 설정됨 - AI 기능 사용 가능
                </Typography>
              </Alert>
            )}

            {/* API Key 표시/입력 영역 */}
            {hasApiKey() ? (
              // API Key가 설정된 경우 - 마스킹된 표시
              <Box sx={{ mb: 2 }}>
                <Box sx={{
                  p: 1,
                  backgroundColor: 'rgba(16, 185, 129, 0.1)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  borderRadius: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  minHeight: '32px'
                }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', flex: 1, minWidth: 0 }}>
                    <KeyIcon sx={{ color: '#10B981', fontSize: 14, mr: 0.5, flexShrink: 0 }} />
                    <Typography
                      variant="caption"
                      sx={{
                        color: '#10B981',
                        fontWeight: 600,
                        fontFamily: 'monospace',
                        fontSize: '0.65rem',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        maxWidth: 'calc(100% - 35px)', // 적절한 여백
                        display: 'block',
                        wordBreak: 'break-all'
                      }}
                    >
                      {tempApiKey.length > 10 
                        ? `${tempApiKey.substring(0, 7)}***${tempApiKey.substring(tempApiKey.length - 4)}`
                        : tempApiKey
                      }
                    </Typography>
                  </Box>
                  <IconButton
                    size="small"
                    onClick={() => setShowApiKey(!showApiKey)}
                    sx={{ 
                      color: '#10B981',
                      ml: 1,
                      flexShrink: 0
                    }}
                  >
                    {showApiKey ? <VisibilityOffIcon fontSize="small" /> : <VisibilityIcon fontSize="small" />}
                  </IconButton>
                </Box>
                
                {/* 전체 API Key 표시 (토글) */}
                {showApiKey && (
                  <Box sx={{
                    mt: 1,
                    p: 1.5,
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: 1,
                    wordBreak: 'break-all'
                  }}>
                    <Typography
                      variant="caption"
                      sx={{
                        color: 'rgba(255, 255, 255, 0.8)',
                        fontFamily: 'monospace',
                        fontSize: '0.7rem',
                        lineHeight: 1.4
                      }}
                    >
                      {tempApiKey}
                    </Typography>
                  </Box>
                )}
              </Box>
            ) : (
              // API Key가 설정되지 않은 경우 - 입력 필드
              <TextField
                fullWidth
                size="small"
                placeholder="sk-..."
                type={showApiKey ? 'text' : 'password'}
                value={tempApiKey}
                onChange={(e) => setTempApiKey(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <KeyIcon sx={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: 16 }} />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        size="small"
                        onClick={() => setShowApiKey(!showApiKey)}
                        sx={{ color: 'rgba(255, 255, 255, 0.5)' }}
                      >
                        {showApiKey ? <VisibilityOffIcon fontSize="small" /> : <VisibilityIcon fontSize="small" />}
                      </IconButton>
                    </InputAdornment>
                  ),
                  sx: {
                    backgroundColor: 'rgba(255, 255, 255, 0.08)',
                    borderRadius: 1,
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'rgba(255, 255, 255, 0.2)',
                    },
                    '&:hover .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'rgba(255, 255, 255, 0.3)',
                    },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                      borderColor: '#3B82F6',
                    },
                    color: 'white',
                    fontSize: '0.875rem'
                  }
                }}
                sx={{ mb: 1 }}
              />
            )}

            {validationError && (
              <Alert 
                severity="error" 
                sx={{ 
                  mb: 1,
                  background: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  color: '#FCA5A5',
                  '& .MuiAlert-icon': {
                    color: '#EF4444'
                  }
                }}
              >
                <Typography variant="caption">
                  {validationError}
                </Typography>
              </Alert>
            )}

            {/* API Key 액션 버튼들 */}
            {hasApiKey() ? (
              // API Key가 설정된 경우 - 변경/삭제 버튼
              <Box sx={{ display: 'flex', gap: 0.5 }}>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={handleApiKeySave}
                  disabled={isValidating}
                  sx={{
                    flex: 1,
                    borderColor: '#3B82F6',
                    color: '#3B82F6',
                    fontSize: '0.65rem',
                    py: 0.5,
                    px: 1,
                    minWidth: 'auto',
                    '&:hover': {
                      borderColor: '#2563EB',
                      backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    },
                    '&:disabled': {
                      borderColor: 'rgba(255, 255, 255, 0.1)',
                      color: 'rgba(255, 255, 255, 0.3)'
                    }
                  }}
                >
                  {isValidating ? '검증' : '변경'}
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => {
                    setTempApiKey('');
                    saveApiKey('');
                  }}
                  sx={{
                    borderColor: '#EF4444',
                    color: '#EF4444',
                    fontSize: '0.65rem',
                    py: 0.5,
                    minWidth: 'auto',
                    px: 1,
                    '&:hover': {
                      borderColor: '#DC2626',
                      backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    }
                  }}
                >
                  삭제
                </Button>
              </Box>
            ) : (
              // API Key가 설정되지 않은 경우 - 저장 버튼
              <Button
                fullWidth
                size="small"
                variant="outlined"
                onClick={handleApiKeySave}
                disabled={isValidating || !tempApiKey.trim()}
                sx={{
                  borderColor: 'rgba(255, 255, 255, 0.3)',
                  color: 'rgba(255, 255, 255, 0.8)',
                  fontSize: '0.75rem',
                  py: 0.5,
                  '&:hover': {
                    borderColor: 'rgba(255, 255, 255, 0.6)',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  },
                  '&:disabled': {
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    color: 'rgba(255, 255, 255, 0.3)'
                  }
                }}
              >
                {isValidating ? '검증 중...' : 'API Key 저장'}
              </Button>
            )}
          </Box>
          
          <Box sx={{ flex: 1 }}>
            <InterestSelector value={interests} onChange={setInterests} />
            <CVUploader onFileChange={setCvFile} />
          </Box>
          
          <Button
            variant="contained"
            fullWidth
            sx={{ 
              mt: 3,
              py: 2,
              fontSize: '1.1rem',
              fontWeight: 700,
              background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
              boxShadow: '0 4px 14px 0 rgba(16, 185, 129, 0.4)',
              '&:hover': {
                background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                boxShadow: '0 6px 20px 0 rgba(16, 185, 129, 0.5)',
                transform: 'translateY(-2px)'
              },
              '&:disabled': {
                background: '#6B7280',
                boxShadow: 'none',
                transform: 'none'
              }
            }}
            disabled={!cvFile || interests.length === 0 || loading || !hasApiKey()}
            onClick={() => onAnalyze(cvFile, interests)}
                      >
              {loading ? "분석 중..." : !hasApiKey() ? "API Key 필요" : "분석 시작"}
            </Button>
        </Box>
      </Paper>
      
      {/* 리사이즈 핸들 */}
      <Box
        ref={resizeRef}
        onMouseDown={handleMouseDown}
        sx={{
          position: 'absolute',
          right: -2,
          top: 0,
          width: 4,
          height: '100%',
          cursor: 'col-resize',
          backgroundColor: 'transparent',
          zIndex: 10,
          '&:hover': {
            backgroundColor: 'rgba(59, 130, 246, 0.2)',
          },
          '&::after': {
            content: '""',
            position: 'absolute',
            left: '50%',
            top: '50%',
            transform: 'translate(-50%, -50%)',
            width: 2,
            height: 40,
            backgroundColor: '#E5E7EB',
            borderRadius: 1,
            opacity: 0,
            transition: 'opacity 0.2s ease',
          },
          '&:hover::after': {
            opacity: 1,
          },
        }}
      />
    </Box>
  );
};

export default Sidebar;
