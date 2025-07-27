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
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Article,
  Search,
  Psychology,
  Science,
  Computer,
  TrendingUp,
  PlayArrow,
  Pause,
  VolumeUp,
  ExpandMore,
  Refresh,
  AutoStories,
  School,
  Science as ScienceIcon,
  Timeline,
  Assessment,
} from '@mui/icons-material';
import { 
  analyzePaper, 
  getRandomPaper, 
  searchPapers, 
  Paper as PaperInterface, 
  PaperAnalysisResponse,
  PaperAnalysisRequest 
} from '../api/papers';

interface FieldOption {
  value: string;
  label: string;
  icon: React.ReactNode;
}

const fieldOptions: FieldOption[] = [
  { value: 'Computer Vision', label: 'Computer Vision', icon: <Computer /> },
  { value: 'Natural Language Processing', label: 'NLP', icon: <Psychology /> },
  { value: 'Machine Learning', label: 'Machine Learning', icon: <Science /> },
  { value: 'Deep Learning', label: 'Deep Learning', icon: <TrendingUp /> },
];

export default function PapersPage() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedField, setSelectedField] = useState<string>('');
  const [papers, setPapers] = useState<PaperInterface[]>([]);
  const [selectedPaper, setSelectedPaper] = useState<PaperInterface | null>(null);
  const [analysisResult, setAnalysisResult] = useState<PaperAnalysisResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [searching, setSearching] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [includeTTS, setIncludeTTS] = useState<boolean>(true);
  const [analysisDepth, setAnalysisDepth] = useState<'basic' | 'detailed' | 'comprehensive'>('detailed');
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [audio, setAudio] = useState<HTMLAudioElement | null>(null);

  useEffect(() => {
    loadRandomPaper();
  }, []);

  useEffect(() => {
    return () => {
      if (audio) {
        audio.pause();
        audio.src = '';
      }
    };
  }, [audio]);

  const loadRandomPaper = async () => {
    try {
      setLoading(true);
      setError(null);
      const paper = await getRandomPaper(selectedField || undefined);
      setPapers([paper]);
      setSelectedPaper(paper);
    } catch (err: any) {
      setError(err.message || '랜덤 논문 로드 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setError('검색어를 입력해주세요.');
      return;
    }

    try {
      setSearching(true);
      setError(null);
      const results = await searchPapers(searchQuery, selectedField || undefined, 10);
      setPapers(results);
      if (results.length > 0) {
        setSelectedPaper(results[0]);
      }
    } catch (err: any) {
      setError(err.message || '논문 검색 중 오류가 발생했습니다.');
    } finally {
      setSearching(false);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedPaper) {
      setError('분석할 논문을 선택해주세요.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setAnalysisResult(null);

      const request: PaperAnalysisRequest = {
        paper_id: selectedPaper.id,
        include_tts: includeTTS,
        analysis_depth: analysisDepth,
      };

      const result = await analyzePaper(request);
      setAnalysisResult(result);
    } catch (err: any) {
      setError(err.message || '논문 분석 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handlePlayAudio = () => {
    if (!analysisResult?.tts_audio_url) return;

    if (audio && isPlaying) {
      audio.pause();
      setIsPlaying(false);
    } else {
      if (audio) {
        audio.src = analysisResult.tts_audio_url;
        audio.play();
        setIsPlaying(true);
      } else {
        const newAudio = new Audio(analysisResult.tts_audio_url);
        newAudio.addEventListener('ended', () => setIsPlaying(false));
        newAudio.play();
        setIsPlaying(true);
        setAudio(newAudio);
      }
    }
  };

  const renderAnalysisSection = (title: string, content: string, icon: React.ReactNode) => (
    <Accordion defaultExpanded>
      <AccordionSummary expandIcon={<ExpandMore />}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {icon}
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            {title}
          </Typography>
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        <Typography variant="body1" sx={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
          {content}
        </Typography>
      </AccordionDetails>
    </Accordion>
  );

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* 헤더 */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
          <Article sx={{ mr: 2, verticalAlign: 'middle' }} />
          논문 분석
        </Typography>
        <Typography variant="h6" color="text.secondary">
          AI로 논문을 체계적으로 분석하고 TTS로 들을 수 있습니다
        </Typography>
      </Box>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' }, gap: 4 }}>
        {/* 왼쪽 패널 - 검색 및 논문 목록 */}
        <Stack spacing={3}>
          {/* 검색 패널 */}
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
              <Search sx={{ mr: 1, verticalAlign: 'middle' }} />
              논문 검색
            </Typography>
            
            <Stack spacing={2}>
              {/* 분야 선택 */}
              <FormControl fullWidth>
                <InputLabel>연구 분야</InputLabel>
                <Select
                  value={selectedField}
                  onChange={(e) => setSelectedField(e.target.value)}
                  label="연구 분야"
                >
                  <MenuItem value="">전체 분야</MenuItem>
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

              {/* 검색어 입력 */}
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  placeholder="논문 제목, 키워드, 저자 등으로 검색"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
                <Button
                  variant="contained"
                  onClick={handleSearch}
                  disabled={searching}
                  startIcon={searching ? <CircularProgress size={20} /> : <Search />}
                >
                  검색
                </Button>
              </Box>

              {/* 랜덤 논문 버튼 */}
              <Button
                variant="outlined"
                onClick={loadRandomPaper}
                disabled={loading}
                startIcon={<Refresh />}
                fullWidth
              >
                랜덤 논문 가져오기
              </Button>
            </Stack>
          </Paper>

          {/* 논문 목록 */}
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
              <AutoStories sx={{ mr: 1, verticalAlign: 'middle' }} />
              논문 목록
            </Typography>
            
            {papers.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Search sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                <Typography color="text.secondary">
                  검색어를 입력하거나 랜덤 논문을 가져와보세요
                </Typography>
              </Box>
            ) : (
              <Stack spacing={2}>
                {papers.map((paper) => (
                  <Card 
                    key={paper.id} 
                    variant={selectedPaper?.id === paper.id ? "elevation" : "outlined"}
                    sx={{ 
                      cursor: 'pointer',
                      '&:hover': { boxShadow: 2 },
                      border: selectedPaper?.id === paper.id ? 2 : 1,
                      borderColor: selectedPaper?.id === paper.id ? 'primary.main' : 'divider'
                    }}
                    onClick={() => setSelectedPaper(paper)}
                  >
                    <CardContent>
                      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                        {paper.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {paper.authors} • {paper.conference} {paper.year}
                      </Typography>
                      <Chip 
                        label={paper.field} 
                        size="small" 
                        color="primary" 
                        variant="outlined"
                        sx={{ mt: 1 }}
                      />
                    </CardContent>
                  </Card>
                ))}
              </Stack>
            )}
          </Paper>
        </Stack>

        {/* 오른쪽 패널 - 분석 설정 및 결과 */}
        <Stack spacing={3}>
          {/* 분석 설정 */}
          {selectedPaper && (
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                <Assessment sx={{ mr: 1, verticalAlign: 'middle' }} />
                분석 설정
              </Typography>
              
              <Stack spacing={2}>
                {/* 선택된 논문 정보 */}
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                      {selectedPaper.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {selectedPaper.authors} • {selectedPaper.conference} {selectedPaper.year}
                    </Typography>
                    <Typography variant="body2" sx={{ 
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                      lineHeight: 1.5
                    }}>
                      {selectedPaper.abstract}
                    </Typography>
                  </CardContent>
                </Card>

                {/* 분석 깊이 설정 */}
                <FormControl fullWidth>
                  <InputLabel>분석 깊이</InputLabel>
                  <Select
                    value={analysisDepth}
                    onChange={(e) => setAnalysisDepth(e.target.value as any)}
                    label="분석 깊이"
                  >
                    <MenuItem value="basic">기본</MenuItem>
                    <MenuItem value="detailed">상세</MenuItem>
                    <MenuItem value="comprehensive">포괄적</MenuItem>
                  </Select>
                </FormControl>

                {/* TTS 설정 */}
                <FormControlLabel
                  control={
                    <Switch
                      checked={includeTTS}
                      onChange={(e) => setIncludeTTS(e.target.checked)}
                    />
                  }
                  label="TTS 음성 생성"
                />

                {/* 분석 버튼 */}
                <Button
                  variant="contained"
                  size="large"
                  onClick={handleAnalyze}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <Psychology />}
                  fullWidth
                >
                  {loading ? '분석 중...' : '논문 분석 시작'}
                </Button>
              </Stack>
            </Paper>
          )}

          {/* 분석 결과 */}
          {analysisResult && (
            <Paper elevation={3} sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h5" sx={{ fontWeight: 600 }}>
                  <Timeline sx={{ mr: 1, verticalAlign: 'middle' }} />
                  분석 결과
                </Typography>
                
                {analysisResult.tts_audio_url && (
                  <IconButton
                    onClick={handlePlayAudio}
                    color="primary"
                    size="large"
                    sx={{ 
                      backgroundColor: 'primary.main',
                      color: 'white',
                      '&:hover': { backgroundColor: 'primary.dark' }
                    }}
                  >
                    {isPlaying ? <Pause /> : <PlayArrow />}
                  </IconButton>
                )}
              </Box>

              <Stack spacing={2}>
                {renderAnalysisSection(
                  "문제 정의",
                  analysisResult.problem_definition,
                  <School />
                )}
                {renderAnalysisSection(
                  "제안 방법",
                  analysisResult.proposed_method,
                  <ScienceIcon />
                )}
                {renderAnalysisSection(
                  "실험 설정",
                  analysisResult.experimental_setup,
                  <Assessment />
                )}
                {renderAnalysisSection(
                  "주요 결과",
                  analysisResult.key_results,
                  <TrendingUp />
                )}
                {renderAnalysisSection(
                  "연구 의의",
                  analysisResult.research_significance,
                  <Psychology />
                )}
              </Stack>
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