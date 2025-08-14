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
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Star as StarIcon,
  Home,
  Upload as UploadIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import { useRouter } from 'next/router';
import CVUploader from '../../components/CVUploader';
import RadarChart from '../../components/RadarChart';
import { analyzeCVFromFile } from '../../api/cv-analysis';
import { useApiKey } from '../../hooks/useApiKey';
import ApiKeySection from '../../components/ApiKeySection';

interface CVAnalysisResult {
  id: string;
  cv_text: string;
  skills: string[];
  experiences: any[];
  strengths: string[];
  weaknesses: string[];
  radar_chart_data: any;
  created_at: string;
}

// 동적으로 fieldOptions 생성하는 함수
const createFieldOptions = (availableFields: any) => {
  console.log('createFieldOptions 호출됨, availableFields:', availableFields, typeof availableFields);
  
  if (!Array.isArray(availableFields) || availableFields.length === 0) {
    console.log('availableFields가 배열이 아니거나 비어있음, 빈 배열 반환');
    return [];
  }
  
  const options = availableFields.map(field => ({
    value: field,
    label: field
  }));
  
  console.log('생성된 options:', options);
  return options;
};

const CVAnalysisPage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [field, setField] = useState('Machine Learning / Deep Learning (ML/DL)');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CVAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [showAllExperiences, setShowAllExperiences] = useState(false);
  const [availableFields, setAvailableFields] = useState<string[]>([]);
  const [fieldsLoading, setFieldsLoading] = useState<boolean>(true);
  const [sidebarWidth, setSidebarWidth] = useState(320);
  const [isResizing, setIsResizing] = useState(false);
  const router = useRouter();
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

  // 분야가 설정되면 초기 필드 설정
  useEffect(() => {
    if (availableFields.length > 0 && !field) {
      setField(availableFields[0] || '');
    }
  }, [availableFields, field]);

  const loadAvailableFields = async () => {
    try {
      setFieldsLoading(true);
      // CV 분석용 하드코딩된 분야 목록
      const fields = [
        "Machine Learning / Deep Learning (ML/DL)",
        "Natural Language Processing (NLP)",
        "Computer Vision (CV)"
      ];
      console.log('CV 분석용 분야 목록:', fields);
      setAvailableFields(fields);
    } catch (err) {
      console.error('분야 목록 로드 실패:', err);
      setAvailableFields([]);
    } finally {
      setFieldsLoading(false);
    }
  };

  const handleGoHome = () => {
    router.push('/');
  };

  const handleFileChange = (file: File | null) => {
    setSelectedFile(file);
    setError(null);
  };

  const handleFieldChange = (event: any) => {
    setField(event.target.value);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError('CV 파일을 업로드해주세요.');
      return;
    }

    if (!hasApiKey()) {
      setError('OpenAI API Key를 먼저 설정해주세요.');
      return;
    }

    setLoading(true);
    setError(null);
    setShowAllExperiences(false); // 분석 시작 시 더보기 상태 초기화

    try {
      const data = await analyzeCVFromFile(selectedFile, field, apiKey);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const isAnalyzeDisabled = !selectedFile || loading || !hasApiKey();

  // 표시할 경험 개수 결정
  const displayedExperiences = result?.experiences?.slice(0, showAllExperiences ? undefined : 3) || [];
  const hasMoreExperiences = result?.experiences && result.experiences.length > 3;

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
          <AssessmentIcon sx={{ mr: 2, verticalAlign: 'middle' }} />
          CV 분석
        </Typography>
        <Typography variant="h6" color="text.secondary">
          AI가 당신의 CV를 분석하여 강점과 개선점을 제시합니다
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
            functionName="CV 분석" 
            description="먼저 OpenAI API Key를 설정해주세요."
          />

          {/* 입력 패널 */}
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
              <UploadIcon sx={{ mr: 1, color: 'primary.main' }} />
              CV 파일 업로드
            </Typography>
            
            <CVUploader onFileChange={handleFileChange} />
            
            <Divider sx={{ my: 3 }} />
            
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>분야 선택</InputLabel>
              <Select
                value={field}
                label="분야 선택"
                onChange={handleFieldChange}
              >
                {fieldsLoading ? (
                  <MenuItem disabled>
                    <CircularProgress size={16} sx={{ mr: 1 }} />
                    분야 로딩 중...
                  </MenuItem>
                ) : (
                  (() => {
                    const options = createFieldOptions(availableFields);
                    console.log('Select 컴포넌트에서 렌더링할 options:', options);
                    return options.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ));
                  })()
                )}
              </Select>
            </FormControl>
            
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

        {/* 오른쪽 패널 - 결과 */}
        <Box>
          {result ? (
            <Stack spacing={3}>
              {/* 경험 섹션 */}
              <Card elevation={3}>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                    <PsychologyIcon sx={{ mr: 1, color: 'primary.main' }} />
                    프로젝트 경험
                    {result.experiences && result.experiences.length > 0 && (
                      <Chip 
                        label={`${result.experiences.length}개`} 
                        size="small" 
                        color="primary" 
                        variant="outlined"
                        sx={{ ml: 1 }}
                      />
                    )}
                  </Typography>
                  <List dense>
                    {displayedExperiences.map((experience, index) => (
                      <ListItem key={index} sx={{ py: 1, px: 0 }}>
                        <ListItemIcon sx={{ minWidth: 32 }}>
                          <StarIcon color="primary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText
                          primary={experience.title}
                          secondary={
                            <Box>
                              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                                {experience.description}
                              </Typography>
                              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                {experience.technologies?.map((tech: string, techIndex: number) => (
                                  <Chip
                                    key={techIndex}
                                    label={tech}
                                    size="small"
                                    variant="outlined"
                                    color="primary"
                                  />
                                ))}
                              </Box>
                            </Box>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                  
                  {/* 더보기/접기 버튼 */}
                  {hasMoreExperiences && (
                    <Box sx={{ mt: 2, textAlign: 'center' }}>
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => setShowAllExperiences(!showAllExperiences)}
                        startIcon={showAllExperiences ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        sx={{
                          color: 'primary.main',
                          borderColor: 'primary.main',
                          '&:hover': {
                            backgroundColor: 'primary.50',
                          },
                        }}
                      >
                        {showAllExperiences ? '접기' : `더보기 (${result.experiences.length - 3}개 더)`}
                      </Button>
                    </Box>
                  )}
                </CardContent>
              </Card>

              {/* 보유 스킬 섹션 */}
              <Card elevation={3}>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                    <StarIcon sx={{ mr: 1, color: 'primary.main' }} />
                    보유 스킬
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {result.skills.map((skill, index) => (
                      <Chip
                        key={index}
                        label={skill}
                        color="primary"
                        variant="outlined"
                        size="small"
                      />
                    ))}
                  </Box>
                </CardContent>
              </Card>

              {/* 강점 섹션 */}
              <Card elevation={3}>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                    <CheckCircleIcon sx={{ mr: 1, color: 'success.main' }} />
                    강점
                  </Typography>
                  <List dense>
                    {result.strengths.map((strength, index) => (
                      <ListItem key={index} sx={{ py: 0.5 }}>
                        <ListItemIcon sx={{ minWidth: 32 }}>
                          <CheckCircleIcon color="success" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary={strength} />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>

              {/* 개선점 섹션 */}
              <Card elevation={3}>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                    <CancelIcon sx={{ mr: 1, color: 'error.main' }} />
                    개선점
                  </Typography>
                  <List dense>
                    {result.weaknesses.map((weakness, index) => (
                      <ListItem key={index} sx={{ py: 0.5 }}>
                        <ListItemIcon sx={{ minWidth: 32 }}>
                          <CancelIcon color="error" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary={weakness} />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>

              {/* 레이더 차트 */}
              {result.radar_chart_data && (
                <Card elevation={3}>
                  <CardContent>
                    <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                      <TrendingUpIcon sx={{ mr: 1, color: 'info.main' }} />
                      능력 평가
                    </Typography>
                    <RadarChart data={result.radar_chart_data} />
                  </CardContent>
                </Card>
              )}
            </Stack>
          ) : (
            <Paper elevation={0} sx={{ p: 6, textAlign: 'center', color: 'text.secondary', minHeight: 400, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
              <PsychologyIcon sx={{ fontSize: 80, mb: 3, opacity: 0.5 }} />
              <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>
                CV 분석 결과
              </Typography>
              <Typography variant="body1" sx={{ maxWidth: 400 }}>
                왼쪽에서 CV 파일을 업로드하고 분석을 시작하세요.
              </Typography>
            </Paper>
          )}
        </Box>
      </Box>
    </Container>
    </Box>
  );
};

export default CVAnalysisPage; 