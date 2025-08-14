import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  TextField,
  Button,
  Chip,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Divider,
  Stack,
  useTheme,
  useMediaQuery,
  Link,
} from '@mui/material';
import {
  TrendingUp,
  Psychology,
  Science,
  Computer,
  Search,
  Article,
  Timeline,
  OpenInNew,
  Home,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { analyzeTrends, TrendAnalysisResponse } from '../../api/trends';
import { getAvailableFields } from '../../api/papers';
import { useRouter } from 'next/router';
import { useApiKey } from '../../hooks/useApiKey';
import ApiKeySection from '../../components/ApiKeySection';

interface FieldOption {
  value: string;
  label: string;
  icon: React.ReactNode;
}

// Field별 아이콘 매핑
const getFieldIcon = (field: string): React.ReactNode => {
  switch (field) {
    case 'Computer Vision (CV)':
      return <Computer />;
    case 'Natural Language Processing (NLP)':
      return <Psychology />;
    case 'Machine Learning / Deep Learning (ML/DL)':
      return <TrendingUp />;
    default:
      return <Science />;
  }
};

// 동적으로 fieldOptions 생성하는 함수
const createFieldOptions = (availableFields: any): FieldOption[] => {
  // 디버깅을 위한 로그
  console.log('availableFields:', availableFields, typeof availableFields);
  
  // 배열이 아닌 경우 빈 배열 반환
  if (!Array.isArray(availableFields) || availableFields.length === 0) {
    console.log('availableFields is not an array or empty, returning empty array');
    return [];
  }
  
  return availableFields.map(field => ({
    value: field,
    label: field,
    icon: getFieldIcon(field)
  }));
};

export default function TrendsPage() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const router = useRouter();
  
  const [selectedField, setSelectedField] = useState<string>('');
  const [keywords, setKeywords] = useState<string[]>([]);
  const [newKeyword, setNewKeyword] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TrendAnalysisResponse | null>(null);
  const [availableFields, setAvailableFields] = useState<string[]>([]);
  const [fieldsLoading, setFieldsLoading] = useState<boolean>(true);
  const [sidebarWidth, setSidebarWidth] = useState(320);
  const [isResizing, setIsResizing] = useState(false);
  const { apiKey, hasApiKey } = useApiKey();

  // 사이드바 리사이즈 관련 상수
  const MIN_SIDEBAR_WIDTH = 256;
  const MAX_SIDEBAR_WIDTH = 480;

  // 리사이즈 핸들러
  const handleMouseDown = () => {
    setIsResizing(true);
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!isResizing) return;

    const newWidth = e.clientX;
    if (newWidth >= MIN_SIDEBAR_WIDTH && newWidth <= MAX_SIDEBAR_WIDTH) {
      setSidebarWidth(newWidth);
    }
  };

  const handleMouseUp = () => {
    setIsResizing(false);
  };

  // 리사이즈 이벤트 리스너
  useEffect(() => {
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
  }, [isResizing]);

  useEffect(() => {
    loadAvailableFields();
  }, []);

  const loadAvailableFields = async () => {
    try {
      setFieldsLoading(true);
      const fields = await getAvailableFields();
      console.log('API에서 받은 fields:', fields, typeof fields);
      setAvailableFields(fields);
    } catch (err) {
      console.error('분야 목록 로드 실패:', err);
      setAvailableFields([]); // 오류 시 빈 배열로 설정
    } finally {
      setFieldsLoading(false);
    }
  };

  const handleAddKeyword = () => {
    if (newKeyword.trim() && !keywords.includes(newKeyword.trim())) {
      setKeywords([...keywords, newKeyword.trim()]);
      setNewKeyword('');
    }
  };

  const handleRemoveKeyword = (keywordToRemove: string) => {
    setKeywords(keywords.filter(keyword => keyword !== keywordToRemove));
  };

  const handleAnalyze = async () => {
    if (!selectedField || keywords.length === 0) {
      setError('분야와 키워드를 선택해주세요.');
      return;
    }

    if (!hasApiKey()) {
      setError('OpenAI API Key를 먼저 설정해주세요.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const analysisResult = await analyzeTrends({
        field: selectedField,
        keywords: keywords,
        limit: 50,
        similarity_threshold: 0.7,
      }, apiKey);
      
      setResult(analysisResult);
    } catch (err: any) {
      setError(err.message || '트렌드 분석 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handlePaperClick = (paper: any) => {
    if (paper.url) {
      window.open(paper.url, '_blank');
    }
  };

  const handleGoHome = () => {
    router.push('/');
  };

  const renderMarkdown = (content: string) => {
    return (
      <Box sx={{ 
        '& h1, & h2, & h3, & h4, & h5, & h6': {
          fontWeight: 600,
          mb: 1,
          mt: 2,
        },
        '& h1': { fontSize: '1.5rem' },
        '& h2': { fontSize: '1.3rem' },
        '& h3': { fontSize: '1.1rem' },
        '& h4, & h5, & h6': { fontSize: '1rem' },
        '& p': {
          mb: 1.5,
          lineHeight: 1.7,
        },
        '& ul, & ol': {
          pl: 2,
          mb: 1.5,
        },
        '& li': {
          mb: 0.5,
        },
        '& strong': {
          fontWeight: 600,
        },
        '& em': {
          fontStyle: 'italic',
        },
        '& code': {
          backgroundColor: 'grey.100',
          px: 0.5,
          py: 0.2,
          borderRadius: 0.5,
          fontSize: '0.875rem',
        },
        '& pre': {
          backgroundColor: 'grey.100',
          p: 1,
          borderRadius: 1,
          overflow: 'auto',
          mb: 1.5,
        },
        '& blockquote': {
          borderLeft: '4px solid',
          borderColor: 'primary.main',
          pl: 2,
          ml: 0,
          my: 1.5,
          fontStyle: 'italic',
        },
      }}>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {content}
        </ReactMarkdown>
      </Box>
    );
  };

  return (
    <Box sx={{ 
      transform: 'scale(0.8)',
      transformOrigin: 'top center',
      width: '125%',
      marginLeft: '-12.5%',
      minHeight: '100vh'
    }}>
      <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* 헤더 */}
      <Box sx={{ mb: 4, textAlign: 'center', position: 'relative' }}>
        {/* 홈 버튼 */}
        <Button
          variant="outlined"
          startIcon={<Home />}
          onClick={handleGoHome}
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            color: 'text.primary',
            borderColor: 'grey.300',
            '&:hover': {
              backgroundColor: 'grey.50',
              borderColor: 'primary.main',
            },
          }}
        >
          홈으로
        </Button>
        
        <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
          <TrendingUp sx={{ mr: 2, verticalAlign: 'middle' }} />
          논문 트렌드 분석
        </Typography>
        <Typography variant="h6" color="text.secondary">
          관심 분야의 최신 연구 동향을 AI로 분석하고 시각화합니다
        </Typography>
      </Box>

      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', lg: `${sidebarWidth}px 1fr` }, 
        gap: 4,
        position: 'relative'
      }}>
        {/* 왼쪽 패널 - 입력 및 설정 */}
        <Stack spacing={3}>
          {/* API Key 설정 패널 */}
          <ApiKeySection 
            functionName="트렌드 분석" 
            description="먼저 OpenAI API Key를 설정해주세요."
          />

          {/* 입력 패널 */}
          <Paper elevation={3} sx={{ p: 2.5 }}>
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
              분석 설정
            </Typography>
            
            {/* 분야 선택 */}
            <Box sx={{ mb: 2.5 }}>
              <Typography variant="subtitle1" gutterBottom>
                연구 분야
              </Typography>
              {fieldsLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                  <CircularProgress size={24} />
                </Box>
              ) : (
                <Box sx={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  gap: 1,
                  '& .field-button': {
                    justifyContent: 'flex-start', 
                    textTransform: 'none',
                    fontWeight: 500,
                    fontSize: '0.875rem',
                    py: 1.5,
                    px: 2,
                    borderRadius: 2,
                    transition: 'all 0.2s ease-in-out',
                    '&.MuiButton-contained': {
                      backgroundColor: 'primary.main',
                      color: 'white',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                      '&:hover': {
                        backgroundColor: 'primary.dark',
                        transform: 'translateY(-1px)',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                      },
                    },
                    '&.MuiButton-outlined': {
                      color: 'text.primary',
                      borderColor: 'grey.300',
                      backgroundColor: 'white',
                      '&:hover': {
                        backgroundColor: 'grey.50',
                        borderColor: 'primary.main',
                        transform: 'translateY(-1px)',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                      },
                    },
                  }
                }}>
                  {createFieldOptions(availableFields).map((field) => (
                  <Button
                    key={field.value}
                    variant={selectedField === field.value ? 'contained' : 'outlined'}
                    startIcon={field.icon}
                    onClick={() => setSelectedField(field.value)}
                    fullWidth
                    className="field-button"
                  >
                    <Box sx={{ flexGrow: 1, textAlign: 'center' }}>
                      {field.label}
                    </Box>
                  </Button>
                                  ))}
                </Box>
              )}
            </Box>

            {/* 키워드 입력 */}
            <Box sx={{ mb: 2.5 }}>
              <Typography variant="subtitle1" gutterBottom>
                관심 키워드
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 1.5 }}>
                <TextField
                  size="small"
                  placeholder="키워드 입력"
                  value={newKeyword}
                  onChange={(e) => setNewKeyword(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddKeyword()}
                  fullWidth
                />
                <Button
                  variant="contained"
                  onClick={handleAddKeyword}
                  disabled={!newKeyword.trim()}
                  sx={{
                    fontWeight: 600,
                    color: 'white',
                    backgroundColor: 'primary.main',
                    whiteSpace: 'nowrap',
                    minWidth: 'auto',
                    px: 2,
                    '&:hover': {
                      backgroundColor: 'primary.dark',
                    },
                    '&:disabled': {
                      backgroundColor: 'grey.300',
                      color: 'white',
                    },
                  }}
                >
                  추가
                </Button>
              </Box>
              
              {/* 선택된 키워드들 */}
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {keywords.map((keyword) => (
                  <Chip
                    key={keyword}
                    label={keyword}
                    onDelete={() => handleRemoveKeyword(keyword)}
                    color="primary"
                    size="small"
                  />
                ))}
              </Box>
            </Box>

            {/* 분석 버튼 */}
            <Button
              variant="contained"
              size="medium"
              fullWidth
              onClick={handleAnalyze}
              disabled={loading || !selectedField || keywords.length === 0 || !hasApiKey()}
              startIcon={loading ? <CircularProgress size={18} /> : <Search />}
              sx={{ 
                py: 1.5,
                fontWeight: 600,
                fontSize: '0.95rem',
                color: 'white',
                backgroundColor: 'primary.main',
                '&:hover': {
                  backgroundColor: 'primary.dark',
                },
                '&:disabled': {
                  backgroundColor: 'grey.300',
                  color: 'white',
                },
              }}
            >
              {loading ? '분석 중...' : !hasApiKey() ? 'API Key 필요' : '트렌드 분석 시작'}
            </Button>

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </Paper>
        </Stack>

        {/* 리사이즈 핸들러 */}
        {!isMobile && (
          <Box
            onMouseDown={handleMouseDown}
            sx={{
              position: 'absolute',
              left: sidebarWidth - 2,
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
        )}

        {/* 오른쪽 패널 - 결과 */}
        <Stack spacing={2.5}>
          {result ? (
            <>
              {/* 트렌드 요약 */}
              <Paper elevation={3} sx={{ p: 2.5 }}>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                  <Timeline sx={{ mr: 1, verticalAlign: 'middle' }} />
                  트렌드 분석 결과
                </Typography>
                <Divider sx={{ mb: 1.5 }} />
                {renderMarkdown(result.trend_summary)}
              </Paper>

              {/* 상위 논문들 */}
              <Paper elevation={3} sx={{ p: 2.5 }}>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                  <Article sx={{ mr: 1, verticalAlign: 'middle' }} />
                  관련 논문 TOP 10
                </Typography>
                <Divider sx={{ mb: 1.5 }} />
                <Stack spacing={2}>
                  {result.top_papers.map((paper, index) => (
                    <Card key={paper.id} variant="outlined">
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                          <Typography 
                            variant="h6" 
                            gutterBottom 
                            sx={{ 
                              fontWeight: 600,
                              flex: 1,
                              cursor: paper.url ? 'pointer' : 'default',
                              '&:hover': paper.url ? {
                                color: 'primary.main',
                                textDecoration: 'underline',
                              } : {},
                            }}
                            onClick={() => handlePaperClick(paper)}
                          >
                            {index + 1}. {paper.title}
                          </Typography>
                          {paper.url && (
                            <OpenInNew 
                              sx={{ 
                                fontSize: 16, 
                                color: 'text.secondary',
                                cursor: 'pointer',
                                '&:hover': { color: 'primary.main' }
                              }} 
                            />
                          )}
                        </Box>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {paper.authors} • {paper.conference} {paper.year}
                        </Typography>
                        <Typography variant="body2" sx={{ 
                          display: '-webkit-box',
                          WebkitLineClamp: 3,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                          lineHeight: 1.5
                        }}>
                          {paper.abstract}
                        </Typography>
                        {paper.similarity_score && (
                          <Chip
                            label={`유사도: ${(paper.similarity_score * 100).toFixed(1)}%`}
                            size="small"
                            color="secondary"
                            sx={{ mt: 1 }}
                          />
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </Stack>
              </Paper>
            </>
          ) : (
            <Paper elevation={3} sx={{ p: 6, textAlign: 'center' }}>
              <Search sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                분석할 분야와 키워드를 선택해주세요
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Dense Retrieval과 LLM을 활용하여 최신 연구 트렌드를 분석합니다
              </Typography>
            </Paper>
          )}
        </Stack>
      </Box>
    </Container>
    </Box>
  );
} 