import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Box,
  Container,
  Typography,
  Paper,
  TextField,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Divider,
  Stack,
  useTheme,
  useMediaQuery,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  FormControlLabel,
  Switch,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Compare,
  Psychology,
  Science,
  Computer,
  TrendingUp,
  ExpandMore,
  Lightbulb,
  School,
  TrendingDown,
  CheckCircle,
  Warning,
  Info,
  AutoStories,
  Psychology as PsychologyIcon,
  Home,
  OpenInNew,
} from '@mui/icons-material';
import { 
  compareMethods, 
  getAvailableFields, 
  MethodComparisonResponse,
  MethodComparisonRequest
} from '../../api/comparison';
import { useRouter } from 'next/router';

interface FieldOption {
  value: string;
  label: string;
  icon: React.ReactNode;
}

const fieldOptions: FieldOption[] = [
  { value: 'Computer Vision (CV)', label: 'Computer Vision (CV)', icon: <Computer /> },
  { value: 'Natural Language Processing (NLP)', label: 'Natural Language Processing (NLP)', icon: <Psychology /> },
  { value: 'Multimodal', label: 'Multimodal', icon: <Science /> },
  { value: 'Machine Learning / Deep Learning (ML/DL)', label: 'Machine Learning / Deep Learning (ML/DL)', icon: <TrendingUp /> },
];

export default function ComparisonPage() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const router = useRouter();
  
  const [userIdea, setUserIdea] = useState<string>('');
  const [selectedField, setSelectedField] = useState<string>('');
  const [similarityThreshold, setSimilarityThreshold] = useState<number>(0.4);
  const [maxSimilarPapers, setMaxSimilarPapers] = useState<number>(10);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<MethodComparisonResponse | null>(null);
  const [availableFields, setAvailableFields] = useState<string[]>([]);

  useEffect(() => {
    loadAvailableFields();
  }, []);



  const handleGoHome = () => {
    router.push('/');
  };

  const loadAvailableFields = async () => {
    try {
      const fields = await getAvailableFields();
      setAvailableFields(fields);
    } catch (err) {
      console.error('분야 목록 로드 실패:', err);
    }
  };



  const handleCompare = async () => {
    if (!userIdea.trim() || !selectedField) {
      setError('연구 아이디어와 분야를 입력해주세요.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setResult(null);

      const request: MethodComparisonRequest = {
        user_idea: userIdea,
        field: selectedField,
        similarity_threshold: similarityThreshold,
        max_similar_papers: maxSimilarPapers,
      };

      const comparisonResult = await compareMethods(request);
      setResult(comparisonResult);
    } catch (err: any) {
      setError(err.message || '방법론 비교 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const renderSimilarPapers = (papers: MethodComparisonResponse['similar_papers']) => (
    <Stack spacing={2}>
      {papers.map((paper, index) => (
        <Card key={paper.id} variant="outlined">
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
              <Typography 
                variant="h6" 
                sx={{ 
                  fontWeight: 600, 
                  flex: 1,
                  cursor: 'pointer',
                  color: 'primary.main',
                  '&:hover': {
                    textDecoration: 'underline',
                    color: 'primary.dark'
                  }
                }}
                onClick={() => {
                  if (paper.url) {
                    window.open(paper.url, '_blank');
                  }
                }}
              >
                {index + 1}. {paper.title}
                {paper.url && <OpenInNew sx={{ ml: 1, fontSize: 16, verticalAlign: 'middle' }} />}
              </Typography>
              <Chip
                label={`${(paper.similarity_score * 100).toFixed(1)}%`}
                color="primary"
                size="small"
                sx={{ ml: 1 }}
              />
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
          </CardContent>
        </Card>
      ))}
    </Stack>
  );

  const renderRecommendations = (recommendations: string[] | undefined) => {
    if (!recommendations || recommendations.length === 0) {
      return (
        <Paper elevation={3} sx={{ p: 2.5, borderRadius: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Box sx={{ 
              width: 40, 
              height: 40, 
              borderRadius: '50%', 
              backgroundColor: 'grey.300', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              mr: 2
            }}>
              <CheckCircle sx={{ color: 'grey.600' }} />
            </Box>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              추천사항
            </Typography>
          </Box>
          <Typography color="text.secondary">
            추천사항을 생성하는 중입니다...
          </Typography>
        </Paper>
      );
    }
    
    return (
      <Paper elevation={3} sx={{ p: 2.5, borderRadius: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box sx={{ 
            width: 40, 
            height: 40, 
            borderRadius: '50%', 
            backgroundColor: 'grey.300', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            mr: 2
          }}>
            <CheckCircle sx={{ color: 'grey.600' }} />
          </Box>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            추천사항
          </Typography>
        </Box>
        <List dense sx={{ p: 0 }}>
          {recommendations.map((recommendation, index) => (
            <ListItem key={index} sx={{ px: 0, py: 0.5 }}>
              <ListItemIcon sx={{ minWidth: 32 }}>
                <Box sx={{ 
                  width: 20, 
                  height: 20, 
                  borderRadius: '50%', 
                  backgroundColor: 'primary.main', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center'
                }}>
                  <CheckCircle sx={{ fontSize: 14, color: 'white' }} />
                </Box>
              </ListItemIcon>
              <ListItemText 
                primary={recommendation}
                primaryTypographyProps={{ 
                  variant: 'body1',
                  sx: { 
                    fontSize: '0.95rem',
                    lineHeight: 1.4,
                    color: 'text.primary'
                  }
                }}
              />
            </ListItem>
          ))}
        </List>
      </Paper>
    );
  };

  return (
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
          <Compare sx={{ mr: 2, verticalAlign: 'middle' }} />
          방법론 비교
        </Typography>
        <Typography variant="h6" color="text.secondary">
          당신의 연구 아이디어와 유사한 논문들을 비교하여 차별화 전략을 제시합니다
        </Typography>
      </Box>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '350px 1fr' }, gap: 4 }}>
        {/* 왼쪽 패널 - 입력 및 설정 */}
        <Stack spacing={3}>
          {/* 입력 패널 */}
          <Paper elevation={3} sx={{ p: 2.5 }}>
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
              <Lightbulb sx={{ mr: 1, verticalAlign: 'middle' }} />
              연구 아이디어
            </Typography>
            
            <Stack spacing={2.5}>
              {/* 분야 선택 */}
              <FormControl fullWidth>
                <InputLabel>연구 분야</InputLabel>
                <Select
                  value={selectedField}
                  onChange={(e) => setSelectedField(e.target.value)}
                  label="연구 분야"
                >
                  <MenuItem value="">분야 선택</MenuItem>
                  {fieldOptions.map((field) => (
                    <MenuItem key={field.value} value={field.value}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {field.icon}
                        {field.label}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* 연구 아이디어 입력 */}
              <TextField
                fullWidth
                multiline
                rows={3}
                placeholder="당신의 연구 아이디어를 자세히 설명해주세요..."
                value={userIdea}
                onChange={(e) => setUserIdea(e.target.value)}
                label="연구 아이디어"
                variant="outlined"
              />

              {/* 유사도 임계값 */}
              <Box>
                <Typography variant="body2" gutterBottom>
                  유사도 임계값: {similarityThreshold}
                </Typography>
                <Slider
                  value={similarityThreshold}
                  onChange={(_, value) => setSimilarityThreshold(value as number)}
                  min={0.3}
                  max={0.9}
                  step={0.05}
                  marks
                  valueLabelDisplay="auto"
                  size="small"
                />
              </Box>

              {/* 최대 논문 수 */}
              <Box>
                <Typography variant="body2" gutterBottom>
                  최대 비교 논문 수: {maxSimilarPapers}개
                </Typography>
                <Slider
                  value={maxSimilarPapers}
                  onChange={(_, value) => setMaxSimilarPapers(value as number)}
                  min={5}
                  max={20}
                  step={1}
                  marks
                  valueLabelDisplay="auto"
                  size="small"
                />
              </Box>

              {/* 비교 버튼 */}
              <Button
                variant="contained"
                size="medium"
                onClick={handleCompare}
                disabled={loading || !userIdea.trim() || !selectedField}
                startIcon={loading ? <CircularProgress size={18} /> : <Compare />}
                fullWidth
                sx={{ py: 1.5 }}
              >
                {loading ? '비교 중...' : '방법론 비교 시작'}
              </Button>
            </Stack>
          </Paper>


        </Stack>

        {/* 오른쪽 패널 - 결과 */}
        <Stack spacing={2.5}>
          {result ? (
            <>
              {/* 비교 분석 */}
              <Paper elevation={3} sx={{ p: 2.5 }}>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                  <PsychologyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  비교 분석
                </Typography>
                <Divider sx={{ mb: 1.5 }} />
                <Box sx={{ lineHeight: 1.7 }}>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {result.comparison_analysis}
                  </ReactMarkdown>
                </Box>
              </Paper>

              {/* 차별화 전략 */}
              <Paper elevation={3} sx={{ p: 2.5 }}>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                  <School sx={{ mr: 1, verticalAlign: 'middle' }} />
                  차별화 전략
                </Typography>
                <Divider sx={{ mb: 1.5 }} />
                <Box sx={{ lineHeight: 1.7 }}>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {result.differentiation_strategy}
                  </ReactMarkdown>
                </Box>
              </Paper>

              {/* 리뷰어 피드백 */}
              <Paper elevation={3} sx={{ p: 2.5 }}>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                  <Warning sx={{ mr: 1, verticalAlign: 'middle' }} />
                  리뷰어 피드백
                </Typography>
                <Divider sx={{ mb: 1.5 }} />
                <Box sx={{ lineHeight: 1.7 }}>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {result.reviewer_feedback}
                  </ReactMarkdown>
                </Box>
              </Paper>

              {/* 추천사항 */}
              <Paper elevation={3} sx={{ p: 2.5 }}>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                  <CheckCircle sx={{ mr: 1, verticalAlign: 'middle' }} />
                  추천사항
                </Typography>
                <Divider sx={{ mb: 1.5 }} />
                {renderRecommendations(result.recommendations)}
              </Paper>

              {/* 유사 논문들 */}
              <Paper elevation={3} sx={{ p: 2.5 }}>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                  <AutoStories sx={{ mr: 1, verticalAlign: 'middle' }} />
                  유사 논문 ({result.similar_papers.length}개)
                </Typography>
                <Divider sx={{ mb: 1.5 }} />
                {renderSimilarPapers(result.similar_papers)}
              </Paper>
            </>
          ) : (
            <Paper elevation={3} sx={{ p: 6, textAlign: 'center' }}>
              <Compare sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                연구 아이디어와 분야를 입력해주세요
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Dense Retrieval과 LLM을 활용하여 유사 연구와 비교 분석합니다
              </Typography>
            </Paper>
          )}

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </Stack>
      </Box>
    </Container>
  );
} 