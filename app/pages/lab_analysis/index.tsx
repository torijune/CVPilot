import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
  Divider,
  Stack,
  useTheme,
  useMediaQuery,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Grid,
  Avatar,
  CardActions,
  Link,
} from '@mui/material';
import {
  School as SchoolIcon,
  Person as PersonIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Star as StarIcon,
  Home,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Business as BusinessIcon,
  Article as ArticleIcon,
  Lightbulb as LightbulbIcon,
  Key as KeyIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
} from '@mui/icons-material';
import { useRouter } from 'next/router';
import { getProfessorsByField, getAllUniversities, analyzeLab, ProfessorInfo, LabAnalysisResult } from '../../api/lab_analysis';
import { useApiKey } from '../../hooks/useApiKey';
import ApiKeySection from '../../components/ApiKeySection';
import ReactMarkdown from 'react-markdown';

const fieldOptions = [
  { value: 'NLP', label: 'Natural Language Processing (NLP)' },
  { value: 'Computer Vision', label: 'Computer Vision (CV)' },
  { value: 'Multimodal', label: 'Multimodal' },
  { value: 'Machine Learning', label: 'Machine Learning / Deep Learning (ML/DL)' }
];

const LabAnalysisPage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [field, setField] = useState('NLP');
  const [university, setUniversity] = useState<string>('');
  const [universities, setUniversities] = useState<string[]>([]);
  const [universitiesLoading, setUniversitiesLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [professorsLoading, setProfessorsLoading] = useState(false);
  const [professors, setProfessors] = useState<ProfessorInfo[]>([]);
  const [selectedProfessor, setSelectedProfessor] = useState<ProfessorInfo | null>(null);
  const [result, setResult] = useState<LabAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showAllPublications, setShowAllPublications] = useState(false);
  const [sidebarWidth, setSidebarWidth] = useState(320);
  const [isResizing, setIsResizing] = useState(false);
  const router = useRouter();
  const { hasApiKey } = useApiKey();

  const handleGoHome = () => {
    router.push('/');
  };

  const handleFieldChange = (event: any) => {
    setField(event.target.value);
    setSelectedProfessor(null);
    setResult(null);
  };

  const handleUniversityChange = (event: any) => {
    setUniversity(event.target.value);
    setSelectedProfessor(null);
    setResult(null);
  };

  const loadUniversities = async () => {
    setUniversitiesLoading(true);
    try {
      const data = await getAllUniversities();
      setUniversities(data.universities);
    } catch (err) {
      console.error('대학 목록 로드 실패:', err);
    } finally {
      setUniversitiesLoading(false);
    }
  };

  const loadProfessors = async () => {
    if (!field) return;

    setProfessorsLoading(true);
    setError(null);

    try {
      const data = await getProfessorsByField(field, university || undefined);
      setProfessors(data.professors);
    } catch (err) {
      setError(err instanceof Error ? err.message : '교수 목록을 불러오는데 실패했습니다.');
    } finally {
      setProfessorsLoading(false);
    }
  };

  const handleProfessorSelect = (professor: ProfessorInfo) => {
    setSelectedProfessor(professor);
    setResult(null);
  };

  const handleAnalyze = async () => {
    if (!selectedProfessor) {
      setError('분석할 교수를 선택해주세요.');
      return;
    }

    setLoading(true);
    setError(null);
    setShowAllPublications(false);

    try {
      const data = await analyzeLab({
        professor_name: selectedProfessor.professor_name,
        university_name: selectedProfessor.university_name,
        field: field
      });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

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
    loadUniversities();
  }, []);

  useEffect(() => {
    loadProfessors();
  }, [field, university]);

  const isAnalyzeDisabled = !selectedProfessor || loading;

  // 표시할 논문 개수 결정
  const displayedPublications = result?.recent_publications?.slice(0, showAllPublications ? undefined : 3) || [];
  const hasMorePublications = result?.recent_publications && result.recent_publications.length > 3;

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
          <SchoolIcon sx={{ mr: 2, verticalAlign: 'middle' }} />
          연구실 분석
        </Typography>
        <Typography variant="h6" color="text.secondary">
          AI가 연구실의 최신 연구 동향을 분석하여 인사이트를 제공합니다
        </Typography>
      </Box>

      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', lg: `${sidebarWidth}px 1fr` }, 
        gap: 4,
        position: 'relative'
      }}>
        {/* 왼쪽 패널 - 설정 및 교수 선택 */}
        <Stack spacing={3}>
          {/* API Key 설정 패널 */}
          <ApiKeySection 
            functionName="연구실 분석" 
            description="먼저 OpenAI API Key를 설정해주세요."
          />

          {/* 설정 패널 */}
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
              <AssessmentIcon sx={{ mr: 1, color: 'primary.main' }} />
              분석 설정
            </Typography>
            
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>연구 분야 선택</InputLabel>
              <Select
                value={field}
                label="연구 분야 선택"
                onChange={handleFieldChange}
              >
                {fieldOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>학교 선택 (선택사항)</InputLabel>
              <Select
                value={university}
                label="학교 선택 (선택사항)"
                onChange={handleUniversityChange}
                disabled={universitiesLoading}
              >
                <MenuItem value="">
                  <em>모든 학교</em>
                </MenuItem>
                {universities.map((uni) => (
                  <MenuItem key={uni} value={uni}>
                    {uni}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {selectedProfessor && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 600 }}>
                  선택된 교수
                </Typography>
                <Card variant="outlined" sx={{ p: 2, backgroundColor: 'primary.50' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <PersonIcon sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      {selectedProfessor.professor_name}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <BusinessIcon sx={{ mr: 1, fontSize: 'small', color: 'text.secondary' }} />
                    <Typography variant="body2" color="text.secondary">
                      {selectedProfessor.university_name}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                    {selectedProfessor.research_areas.slice(0, 3).map((area, areaIndex) => (
                      <Chip
                        key={areaIndex}
                        label={area}
                        size="small"
                        variant="outlined"
                        color="primary"
                      />
                    ))}
                    {selectedProfessor.research_areas.length > 3 && (
                      <Chip
                        label={`+${selectedProfessor.research_areas.length - 3}`}
                        size="small"
                        variant="outlined"
                        color="secondary"
                      />
                    )}
                  </Box>
                  
                  {selectedProfessor.url && (
                    <Link
                      href={selectedProfessor.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      sx={{
                        fontSize: '0.75rem',
                        color: 'primary.main',
                        textDecoration: 'none',
                        display: 'flex',
                        alignItems: 'center',
                        '&:hover': {
                          textDecoration: 'underline'
                        }
                      }}
                    >
                      연구실 홈페이지 →
                    </Link>
                  )}
                </Card>
              </Box>
            )}
            
            <Button
              variant="contained"
              fullWidth
              size="large"
              onClick={handleAnalyze}
              disabled={isAnalyzeDisabled}
              sx={{
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 600,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
                },
                '&:disabled': {
                  background: 'grey.300',
                },
              }}
            >
              {loading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                '분석 시작'
              )}
            </Button>
          </Paper>

          {/* 에러 메시지 */}
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
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

        {/* 오른쪽 패널 - 교수 목록 및 결과 */}
        <Box>
          {!result ? (
            <Stack spacing={3}>
              {/* 교수 목록 */}
              <Card elevation={3}>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                    <PersonIcon sx={{ mr: 1, color: 'primary.main' }} />
                    교수 목록
                    {professors.length > 0 && (
                      <Chip 
                        label={`${professors.length}명`} 
                        size="small" 
                        color="primary" 
                        variant="outlined"
                        sx={{ ml: 1 }}
                      />
                    )}
                  </Typography>
                  
                  {professorsLoading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                      <CircularProgress />
                    </Box>
                  ) : professors.length > 0 ? (
                    <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)' }, gap: 2 }}>
                      {professors.map((professor, index) => (
                        <Box key={index}>
                          <Card 
                            variant="outlined"
                            sx={{
                              cursor: 'pointer',
                              transition: 'all 0.3s ease',
                              border: selectedProfessor?.professor_name === professor.professor_name 
                                ? '2px solid primary.main' 
                                : '1px solid grey.300',
                              backgroundColor: selectedProfessor?.professor_name === professor.professor_name 
                                ? 'primary.50' 
                                : 'background.paper',
                              '&:hover': {
                                border: '2px solid primary.main',
                                backgroundColor: 'primary.50',
                                transform: 'translateY(-2px)'
                              }
                            }}
                            onClick={() => handleProfessorSelect(professor)}
                          >
                                                        <CardContent sx={{ p: 2 }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Avatar sx={{ width: 32, height: 32, mr: 1, bgcolor: 'primary.main' }}>
                                  <PersonIcon />
                                </Avatar>
                                <Box>
                                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                                    {professor.professor_name}
                                  </Typography>
                                  <Typography variant="caption" color="text.secondary">
                                    {professor.university_name}
                                  </Typography>
                                </Box>
                              </Box>
                              
                              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                                {professor.research_areas.slice(0, 3).map((area, areaIndex) => (
                                  <Chip
                                    key={areaIndex}
                                    label={area}
                                    size="small"
                                    variant="outlined"
                                    color="primary"
                                  />
                                ))}
                                {professor.research_areas.length > 3 && (
                                  <Chip
                                    label={`+${professor.research_areas.length - 3}`}
                                    size="small"
                                    variant="outlined"
                                    color="secondary"
                                  />
                                )}
                              </Box>
                              
                              <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                                주요 분야: {professor.primary_category}
                              </Typography>
                              
                              {professor.url && (
                                <Link
                                  href={professor.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  sx={{
                                    fontSize: '0.75rem',
                                    color: 'primary.main',
                                    textDecoration: 'none',
                                    '&:hover': {
                                      textDecoration: 'underline'
                                    }
                                  }}
                                  onClick={(e) => e.stopPropagation()}
                                >
                                  연구실 홈페이지 →
                                </Link>
                              )}
                            </CardContent>
                           </Card>
                         </Box>
                       ))}
                     </Box>
                  ) : (
                    <Paper elevation={0} sx={{ p: 4, textAlign: 'center', color: 'text.secondary' }}>
                      <PersonIcon sx={{ fontSize: 48, mb: 2, opacity: 0.5 }} />
                      <Typography variant="h6" sx={{ mb: 1 }}>
                        교수를 찾을 수 없습니다
                      </Typography>
                      <Typography variant="body2">
                        다른 연구 분야를 선택해보세요.
                      </Typography>
                    </Paper>
                  )}
                </CardContent>
              </Card>
            </Stack>
                    ) : (
            <Stack spacing={3}>
              {/* 연구 방향 및 특징 */}
              <Card elevation={3}>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                    <LightbulbIcon sx={{ mr: 1, color: 'info.main' }} />
                    연구 방향 및 특징
                  </Typography>
                  <Box sx={{ 
                    '& h1, & h2, & h3, & h4, & h5, & h6': { 
                      color: 'text.primary',
                      fontWeight: 600,
                      mb: 2,
                      mt: 3,
                      fontSize: '1.1rem'
                    },
                    '& p': { 
                      mb: 1.5,
                      lineHeight: 1.8,
                      fontSize: '0.95rem'
                    },
                    '& ul, & ol': {
                      pl: 3,
                      mb: 2,
                      '& li': {
                        mb: 0.8,
                        lineHeight: 1.6,
                        fontSize: '0.95rem'
                      }
                    },
                    '& strong': {
                      fontWeight: 600,
                      color: 'primary.main'
                    },
                    '& em': {
                      fontStyle: 'italic',
                      color: 'text.secondary'
                    }
                  }}>
                    <ReactMarkdown>
                      {result.analysis_summary}
                    </ReactMarkdown>
                  </Box>
                </CardContent>
              </Card>

              {/* 연구 트렌드 */}
              <Card elevation={3}>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                    <TrendingUpIcon sx={{ mr: 1, color: 'success.main' }} />
                    연구 트렌드
                  </Typography>
                  <Box sx={{ 
                    '& h1, & h2, & h3, & h4, & h5, & h6': { 
                      color: 'text.primary',
                      fontWeight: 600,
                      mb: 2,
                      mt: 3,
                      fontSize: '1.1rem'
                    },
                    '& p': { 
                      mb: 1.5,
                      lineHeight: 1.8,
                      fontSize: '0.95rem'
                    },
                    '& ul, & ol': {
                      pl: 3,
                      mb: 2,
                      '& li': {
                        mb: 0.8,
                        lineHeight: 1.6,
                        fontSize: '0.95rem'
                      }
                    },
                    '& strong': {
                      fontWeight: 600,
                      color: 'primary.main'
                    },
                    '& em': {
                      fontStyle: 'italic',
                      color: 'text.secondary'
                    }
                  }}>
                    <ReactMarkdown>
                      {result.research_trends}
                    </ReactMarkdown>
                  </Box>
                </CardContent>
              </Card>

              {/* 연구 계획 및 전략 */}
              <Card elevation={3}>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                    <LightbulbIcon sx={{ mr: 1, color: 'warning.main' }} />
                    연구 계획 및 전략
                  </Typography>
                  <Box sx={{ 
                    '& h1, & h2, & h3, & h4, & h5, & h6': { 
                      color: 'text.primary',
                      fontWeight: 600,
                      mb: 2,
                      mt: 3,
                      fontSize: '1.1rem'
                    },
                    '& p': { 
                      mb: 1.5,
                      lineHeight: 1.8,
                      fontSize: '0.95rem'
                    },
                    '& ul, & ol': {
                      pl: 3,
                      mb: 2,
                      '& li': {
                        mb: 0.8,
                        lineHeight: 1.6,
                        fontSize: '0.95rem'
                      }
                    },
                    '& strong': {
                      fontWeight: 600,
                      color: 'primary.main'
                    },
                    '& em': {
                      fontStyle: 'italic',
                      color: 'text.secondary'
                    }
                  }}>
                    <ReactMarkdown>
                      {result.key_insights}
                    </ReactMarkdown>
                  </Box>
                </CardContent>
              </Card>

              {/* 최신 논문 */}
              <Card elevation={3}>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                    <ArticleIcon sx={{ mr: 1, color: 'primary.main' }} />
                    최신 논문
                    {result.recent_publications && result.recent_publications.length > 0 && (
                      <Chip 
                        label={`${result.recent_publications.length}개`} 
                        size="small" 
                        color="primary" 
                        variant="outlined"
                        sx={{ ml: 1 }}
                      />
                    )}
                  </Typography>
                  <List dense>
                    {displayedPublications.map((publication, index) => (
                      <ListItem key={index} sx={{ py: 2, px: 0 }}>
                        <ListItemIcon sx={{ minWidth: 32, alignSelf: 'flex-start', mt: 0.5 }}>
                          <ArticleIcon color="primary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText 
                          primary={
                            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: 'text.primary' }}>
                              {publication.title}
                            </Typography>
                          }
                          secondary={
                            <Typography variant="body2" sx={{ lineHeight: 1.6, color: 'text.secondary' }}>
                              {publication.abstract}
                            </Typography>
                          }
                          sx={{ 
                            '& .MuiListItemText-secondary': {
                              fontSize: '0.9rem',
                              lineHeight: 1.4
                            }
                          }}
                        />
                      </ListItem>
                    ))}
                  </List>
                  
                  {/* 더보기/접기 버튼 */}
                  {hasMorePublications && (
                    <Box sx={{ mt: 2, textAlign: 'center' }}>
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => setShowAllPublications(!showAllPublications)}
                        startIcon={showAllPublications ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        sx={{
                          color: 'primary.main',
                          borderColor: 'primary.main',
                          '&:hover': {
                            backgroundColor: 'primary.50',
                          },
                        }}
                      >
                        {showAllPublications ? '접기' : `더보기 (${result.recent_publications.length - 3}개 더)`}
                      </Button>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Stack>
          )}
        </Box>
      </Box>
    </Container>
    </Box>
  );
};

export default LabAnalysisPage;
