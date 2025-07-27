import React, { useState, useEffect } from 'react';
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
  Timeline,
  Assessment,
  Psychology as PsychologyIcon,
} from '@mui/icons-material';
import { 
  compareMethods, 
  getAvailableFields, 
  getFieldStatistics,
  getResearchTrends,
  MethodComparisonResponse,
  MethodComparisonRequest,
  FieldStatistics,
  ResearchTrends
} from '../api/comparison';

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
  
  const [userIdea, setUserIdea] = useState<string>('');
  const [selectedField, setSelectedField] = useState<string>('');
  const [similarityThreshold, setSimilarityThreshold] = useState<number>(0.8);
  const [maxSimilarPapers, setMaxSimilarPapers] = useState<number>(10);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<MethodComparisonResponse | null>(null);
  const [fieldStats, setFieldStats] = useState<FieldStatistics | null>(null);
  const [researchTrends, setResearchTrends] = useState<ResearchTrends | null>(null);
  const [availableFields, setAvailableFields] = useState<string[]>([]);

  useEffect(() => {
    loadAvailableFields();
  }, []);

  useEffect(() => {
    if (selectedField) {
      loadFieldStatistics();
      loadResearchTrends();
    }
  }, [selectedField]);

  const loadAvailableFields = async () => {
    try {
      const fields = await getAvailableFields();
      setAvailableFields(fields);
    } catch (err) {
      console.error('분야 목록 로드 실패:', err);
    }
  };

  const loadFieldStatistics = async () => {
    try {
      const stats = await getFieldStatistics(selectedField);
      setFieldStats(stats);
    } catch (err) {
      console.error('분야 통계 로드 실패:', err);
    }
  };

  const loadResearchTrends = async () => {
    try {
      const trends = await getResearchTrends(selectedField);
      setResearchTrends(trends);
    } catch (err) {
      console.error('연구 트렌드 로드 실패:', err);
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
              <Typography variant="h6" sx={{ fontWeight: 600, flex: 1 }}>
                {index + 1}. {paper.title}
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

  const renderRecommendations = (recommendations: string[]) => (
    <List>
      {recommendations.map((recommendation, index) => (
        <ListItem key={index} sx={{ px: 0 }}>
          <ListItemIcon>
            <CheckCircle color="primary" />
          </ListItemIcon>
          <ListItemText 
            primary={recommendation}
            primaryTypographyProps={{ variant: 'body1' }}
          />
        </ListItem>
      ))}
    </List>
  );

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* 헤더 */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
          <Compare sx={{ mr: 2, verticalAlign: 'middle' }} />
          방법론 비교
        </Typography>
        <Typography variant="h6" color="text.secondary">
          당신의 연구 아이디어와 유사한 논문들을 비교하여 차별화 전략을 제시합니다
        </Typography>
      </Box>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' }, gap: 4 }}>
        {/* 왼쪽 패널 - 입력 및 설정 */}
        <Stack spacing={3}>
          {/* 입력 패널 */}
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
              <Lightbulb sx={{ mr: 1, verticalAlign: 'middle' }} />
              연구 아이디어
            </Typography>
            
            <Stack spacing={3}>
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
                rows={4}
                placeholder="당신의 연구 아이디어를 자세히 설명해주세요..."
                value={userIdea}
                onChange={(e) => setUserIdea(e.target.value)}
                label="연구 아이디어"
                variant="outlined"
              />

              {/* 유사도 임계값 */}
              <Box>
                <Typography gutterBottom>
                  유사도 임계값: {similarityThreshold}
                </Typography>
                <Slider
                  value={similarityThreshold}
                  onChange={(_, value) => setSimilarityThreshold(value as number)}
                  min={0.5}
                  max={1.0}
                  step={0.05}
                  marks
                  valueLabelDisplay="auto"
                />
              </Box>

              {/* 최대 논문 수 */}
              <Box>
                <Typography gutterBottom>
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
                />
              </Box>

              {/* 비교 버튼 */}
              <Button
                variant="contained"
                size="large"
                onClick={handleCompare}
                disabled={loading || !userIdea.trim() || !selectedField}
                startIcon={loading ? <CircularProgress size={20} /> : <Compare />}
                fullWidth
              >
                {loading ? '비교 중...' : '방법론 비교 시작'}
              </Button>
            </Stack>
          </Paper>

          {/* 분야 통계 */}
          {fieldStats && (
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                <Assessment sx={{ mr: 1, verticalAlign: 'middle' }} />
                분야 통계
              </Typography>
              
              <Stack spacing={2}>
                <Box>
                  <Typography variant="h6" color="primary">
                    총 논문 수: {fieldStats.total_papers}개
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="subtitle1" gutterBottom>
                    연도별 분포
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {Object.entries(fieldStats.year_distribution)
                      .sort(([a], [b]) => parseInt(b) - parseInt(a))
                      .slice(0, 5)
                      .map(([year, count]) => (
                        <Chip
                          key={year}
                          label={`${year}: ${count}개`}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                  </Box>
                </Box>
              </Stack>
            </Paper>
          )}

          {/* 연구 트렌드 */}
          {researchTrends && (
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                <Timeline sx={{ mr: 1, verticalAlign: 'middle' }} />
                연구 트렌드
              </Typography>
              
              <Stack spacing={2}>
                <Box>
                  <Typography variant="h6" color="primary">
                    최근 논문: {researchTrends.recent_papers_count}개
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="subtitle1" gutterBottom>
                    연도별 트렌드
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    {Object.entries(researchTrends.yearly_trend).map(([year, count]) => (
                      <Chip
                        key={year}
                        label={`${year}: ${count}개`}
                        size="small"
                        color="secondary"
                      />
                    ))}
                  </Box>
                </Box>
              </Stack>
            </Paper>
          )}
        </Stack>

        {/* 오른쪽 패널 - 결과 */}
        <Stack spacing={3}>
          {result ? (
            <>
              {/* 비교 분석 */}
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                  <PsychologyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  비교 분석
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Typography variant="body1" sx={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                  {result.comparison_analysis}
                </Typography>
              </Paper>

              {/* 차별화 전략 */}
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                  <School sx={{ mr: 1, verticalAlign: 'middle' }} />
                  차별화 전략
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Typography variant="body1" sx={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                  {result.differentiation_strategy}
                </Typography>
              </Paper>

              {/* 추천사항 */}
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                  <CheckCircle sx={{ mr: 1, verticalAlign: 'middle' }} />
                  추천사항
                </Typography>
                <Divider sx={{ mb: 2 }} />
                {renderRecommendations(result.recommendations)}
              </Paper>

              {/* 유사 논문들 */}
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                  <AutoStories sx={{ mr: 1, verticalAlign: 'middle' }} />
                  유사 논문 ({result.similar_papers.length}개)
                </Typography>
                <Divider sx={{ mb: 2 }} />
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