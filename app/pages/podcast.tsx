import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton
} from '@mui/material';
import {
  Podcasts as PodcastsIcon,
  PlayArrow as PlayArrowIcon,
  Pause as PauseIcon,
  Download as DownloadIcon,
  Article as ArticleIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material';

interface PodcastResult {
  id: string;
  field: string;
  papers: Array<{
    title: string;
    abstract: string;
    authors: string[];
  }>;
  analysis_text: string;
  audio_file_path: string;
  duration_seconds: number;
  created_at: string;
}

const PodcastPage: React.FC = () => {
  const [field, setField] = useState('Machine Learning / Deep Learning (ML/DL)');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PodcastResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const fields = [
    'Natural Language Processing (NLP)',
    'Computer Vision (CV)',
    'Multimodal',
    'Machine Learning / Deep Learning (ML/DL)'
  ];

  const handleGeneratePodcast = async () => {
    setLoading(true);
    setError(null);

    try {
      // 실제로는 Podcast API를 호출
      // 현재는 모의 데이터 사용
      const mockResult: PodcastResult = {
        id: 'podcast-1',
        field: field,
        papers: [
          {
            title: 'Attention Is All You Need',
            abstract: 'We propose a new simple network architecture, the Transformer, based solely on attention mechanisms...',
            authors: ['Ashish Vaswani', 'Noam Shazeer', 'Niki Parmar']
          },
          {
            title: 'BERT: Pre-training of Deep Bidirectional Transformers',
            abstract: 'We introduce a new language representation model called BERT...',
            authors: ['Jacob Devlin', 'Ming-Wei Chang', 'Kenton Lee']
          }
        ],
        analysis_text: `안녕하세요! 오늘은 ${field} 분야의 최신 연구 동향을 살펴보겠습니다.

먼저, Attention Is All You Need 논문에서는 Transformer 아키텍처를 제안했습니다. 이는 기존의 RNN 기반 모델들의 한계를 극복하고, 병렬 처리 가능한 attention 메커니즘을 도입했습니다.

다음으로, BERT 논문에서는 양방향 Transformer를 활용한 언어 모델 사전 학습 방법을 제시했습니다. 이는 다양한 자연어 처리 태스크에서 뛰어난 성능을 보여주었습니다.

이러한 연구들은 현재 AI 분야의 핵심 기술로 자리잡고 있으며, 많은 후속 연구들이 이어지고 있습니다.`,
        audio_file_path: '/audio/podcast_sample.mp3',
        duration_seconds: 180,
        created_at: new Date().toISOString()
      };

      setResult(mockResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
    // 실제로는 오디오 재생/일시정지 로직 구현
  };

  const handleDownload = () => {
    // 실제로는 오디오 파일 다운로드 로직 구현
    console.log('Downloading audio file...');
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', py: 4 }}>
      <Box sx={{ maxWidth: 1200, mx: 'auto', px: 3 }}>
        {/* 헤더 */}
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Typography variant="h3" sx={{ mb: 2, fontWeight: 700 }}>
            데일리 페이퍼 팟캐스트
          </Typography>
          <Typography variant="h6" color="text.secondary">
            AI가 분석한 최신 논문들을 음성으로 들을 수 있습니다
          </Typography>
        </Box>

        <Grid container spacing={4}>
          {/* 입력 섹션 */}
          <Grid item xs={12} md={4}>
            <Paper elevation={0} sx={{ p: 4, height: 'fit-content' }}>
              <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
                팟캐스트 생성
              </Typography>

              <TextField
                select
                fullWidth
                label="분야 선택"
                value={field}
                onChange={(e) => setField(e.target.value)}
                sx={{ mb: 3 }}
              >
                {fields.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </TextField>

              <Button
                variant="contained"
                fullWidth
                size="large"
                onClick={handleGeneratePodcast}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <PodcastsIcon />}
                sx={{ py: 1.5 }}
              >
                {loading ? '팟캐스트 생성 중...' : '팟캐스트 생성'}
              </Button>

              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}
            </Paper>
          </Grid>

          {/* 결과 섹션 */}
          <Grid item xs={12} md={8}>
            {result ? (
              <Box>
                {/* 오디오 플레이어 */}
                <Card sx={{ mb: 3 }}>
                  <CardContent>
                    <Typography variant="h5" sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
                      <PodcastsIcon sx={{ mr: 1, color: 'primary.main' }} />
                      오디오 플레이어
                    </Typography>
                    
                    <Box sx={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: 2,
                      p: 3,
                      bgcolor: 'grey.50',
                      borderRadius: 2
                    }}>
                      <IconButton 
                        onClick={handlePlayPause}
                        sx={{ 
                          bgcolor: 'primary.main', 
                          color: 'white',
                          '&:hover': { bgcolor: 'primary.dark' }
                        }}
                      >
                        {isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
                      </IconButton>
                      
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {field} 분야 최신 논문 분석
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          재생 시간: {formatDuration(result.duration_seconds)}
                        </Typography>
                      </Box>
                      
                      <IconButton onClick={handleDownload} color="primary">
                        <DownloadIcon />
                      </IconButton>
                    </Box>
                  </CardContent>
                </Card>

                {/* 분석 텍스트 */}
                <Card sx={{ mb: 3 }}>
                  <CardContent>
                    <Typography variant="h5" sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
                      <ArticleIcon sx={{ mr: 1, color: 'info.main' }} />
                      분석 내용
                    </Typography>
                    <Typography variant="body1" sx={{ lineHeight: 1.8, whiteSpace: 'pre-line' }}>
                      {result.analysis_text}
                    </Typography>
                  </CardContent>
                </Card>

                {/* 논문 목록 */}
                <Card>
                  <CardContent>
                    <Typography variant="h5" sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
                      <TrendingUpIcon sx={{ mr: 1, color: 'success.main' }} />
                      분석된 논문들
                    </Typography>
                    <List>
                      {result.papers.map((paper, index) => (
                        <ListItem key={index} sx={{ 
                          border: '1px solid',
                          borderColor: 'grey.200',
                          borderRadius: 2,
                          mb: 2,
                          flexDirection: 'column',
                          alignItems: 'flex-start'
                        }}>
                          <ListItemText
                            primary={
                              <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                                {paper.title}
                              </Typography>
                            }
                            secondary={
                              <Box>
                                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                                  {paper.abstract}
                                </Typography>
                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                  {paper.authors.map((author, authorIndex) => (
                                    <Chip
                                      key={authorIndex}
                                      label={author}
                                      size="small"
                                      variant="outlined"
                                    />
                                  ))}
                                </Box>
                              </Box>
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  </CardContent>
                </Card>
              </Box>
            ) : (
              <Paper elevation={0} sx={{ p: 4, textAlign: 'center', color: 'text.secondary' }}>
                <PodcastsIcon sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
                <Typography variant="h6" sx={{ mb: 1 }}>
                  팟캐스트 결과
                </Typography>
                <Typography variant="body2">
                  왼쪽에서 분야를 선택하고 팟캐스트를 생성해보세요.
                </Typography>
              </Paper>
            )}
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default PodcastPage; 