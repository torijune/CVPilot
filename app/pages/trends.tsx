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
} from '@mui/material';
import {
  TrendingUp,
  Psychology,
  Science,
  Computer,
  Search,
  Cloud,
  Article,
  Timeline,
} from '@mui/icons-material';
import { analyzeTrends, getAvailableFields, TrendAnalysisResponse } from '../api/trends';

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

export default function TrendsPage() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [selectedField, setSelectedField] = useState<string>('');
  const [keywords, setKeywords] = useState<string[]>([]);
  const [newKeyword, setNewKeyword] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TrendAnalysisResponse | null>(null);
  const [availableFields, setAvailableFields] = useState<string[]>([]);

  useEffect(() => {
    loadAvailableFields();
  }, []);

  const loadAvailableFields = async () => {
    try {
      const fields = await getAvailableFields();
      setAvailableFields(fields);
    } catch (err) {
      console.error('분야 목록 로드 실패:', err);
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

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const analysisResult = await analyzeTrends({
        field: selectedField,
        keywords: keywords,
        limit: 50,
        similarity_threshold: 0.7,
      });
      
      setResult(analysisResult);
    } catch (err: any) {
      setError(err.message || '트렌드 분석 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const renderWordCloud = (wordcloudData: Record<string, number>) => {
    const sortedWords = Object.entries(wordcloudData)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 20);

    return (
      <Box sx={{ mt: 2 }}>
        <Typography variant="h6" gutterBottom>
          인기 키워드
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {sortedWords.map(([word, count]) => (
            <Chip
              key={word}
              label={`${word} (${count})`}
              size="small"
              color="primary"
              variant="outlined"
              sx={{
                fontSize: Math.max(12, Math.min(16, 12 + count / 10)),
                fontWeight: 'bold',
              }}
            />
          ))}
        </Box>
      </Box>
    );
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* 헤더 */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
          <TrendingUp sx={{ mr: 2, verticalAlign: 'middle' }} />
          논문 트렌드 분석
        </Typography>
        <Typography variant="h6" color="text.secondary">
          관심 분야의 최신 연구 동향을 AI로 분석하고 시각화합니다
        </Typography>
      </Box>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 2fr' }, gap: 4 }}>
        {/* 입력 패널 */}
        <Box>
          <Paper elevation={3} sx={{ p: 3, height: 'fit-content' }}>
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
              분석 설정
            </Typography>
            
            {/* 분야 선택 */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                연구 분야
              </Typography>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1 }}>
                {fieldOptions.map((field) => (
                  <Button
                    key={field.value}
                    variant={selectedField === field.value ? 'contained' : 'outlined'}
                    startIcon={field.icon}
                    onClick={() => setSelectedField(field.value)}
                    fullWidth
                    sx={{ justifyContent: 'flex-start', textTransform: 'none' }}
                  >
                    {field.label}
                  </Button>
                ))}
              </Box>
            </Box>

            {/* 키워드 입력 */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                관심 키워드
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
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
              size="large"
              fullWidth
              onClick={handleAnalyze}
              disabled={loading || !selectedField || keywords.length === 0}
              startIcon={loading ? <CircularProgress size={20} /> : <Search />}
              sx={{ py: 1.5 }}
            >
              {loading ? '분석 중...' : '트렌드 분석 시작'}
            </Button>

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </Paper>
        </Box>

        {/* 결과 패널 */}
        <Box>
          {result ? (
            <Stack spacing={3}>
              {/* 트렌드 요약 */}
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                  <Timeline sx={{ mr: 1, verticalAlign: 'middle' }} />
                  트렌드 분석 결과
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Typography variant="body1" sx={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                  {result.trend_summary}
                </Typography>
              </Paper>

              {/* 워드클라우드 */}
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                  <Cloud sx={{ mr: 1, verticalAlign: 'middle' }} />
                  키워드 분석
                </Typography>
                <Divider sx={{ mb: 2 }} />
                {renderWordCloud(result.wordcloud_data)}
              </Paper>

              {/* 상위 논문들 */}
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                  <Article sx={{ mr: 1, verticalAlign: 'middle' }} />
                  관련 논문 TOP 10
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Stack spacing={2}>
                  {result.top_papers.map((paper, index) => (
                    <Card key={paper.id} variant="outlined">
                      <CardContent>
                        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                          {index + 1}. {paper.title}
                        </Typography>
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
            </Stack>
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
        </Box>
      </Box>
    </Container>
  );
} 