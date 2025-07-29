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
  Chip,
  CircularProgress,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  Podcasts as PodcastIcon,
  PlayArrow as PlayArrowIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  Download as DownloadIcon,
  Home,
  Mic as MicIcon,
} from '@mui/icons-material';
import { useRouter } from 'next/router';
import { generatePodcast, getPodcastAnalysis, getAvailableFields } from '../../api/podcast';

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
  const [selectedPapers, setSelectedPapers] = useState<any[]>([]);
  const [field, setField] = useState('Machine Learning / Deep Learning (ML/DL)');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PodcastResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [availableFields, setAvailableFields] = useState<string[]>([
    'Natural Language Processing (NLP)',
    'Computer Vision (CV)',
    'Multimodal',
    'Machine Learning / Deep Learning (ML/DL)'
  ]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null);
  const router = useRouter();

  // 사용 가능한 분야 목록 로드
  useEffect(() => {
    const loadFields = async () => {
      try {
        const response = await getAvailableFields();
        if (response.fields && response.fields.length > 0) {
          setAvailableFields(response.fields);
        }
      } catch (err) {
        console.error('분야 목록 로드 실패:', err);
        // API 호출 실패 시 기본 분야 목록 유지
      }
    };
    loadFields();
  }, []);

  const handleGoHome = () => {
    router.push('/');
  };

  const handleGeneratePodcast = async () => {
    setLoading(true);
    setError(null);

    try {
      // 실제 API 호출 (papers 없이 field만 전송하면 DB에서 랜덤으로 가져옴)
      const response = await generatePodcast(field, []);
      
      if (response.success) {
        // 분석 완료까지 대기 (실제로는 폴링 또는 웹소켓 사용)
        setTimeout(async () => {
          try {
            const analysisResult = await getPodcastAnalysis(response.analysis_id);
            setResult(analysisResult);
          } catch (err) {
            setError('분석 결과를 가져오는데 실패했습니다.');
          }
        }, 5000); // 5초 후 결과 조회 (실제로는 더 정교한 처리 필요)
      } else {
        setError('팟캐스트 생성에 실패했습니다.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handlePlayPause = () => {
    if (!result?.audio_file_path) {
      console.error('오디오 파일 경로가 없습니다.');
      return;
    }

    if (!audioElement) {
      // 새로운 오디오 엘리먼트 생성
      const audio = new Audio(result.audio_file_path);
      audio.addEventListener('ended', () => setIsPlaying(false));
      audio.addEventListener('error', (e) => {
        console.error('오디오 재생 오류:', e);
        setIsPlaying(false);
      });
      setAudioElement(audio);
    }

    if (isPlaying) {
      // 일시정지
      audioElement?.pause();
      setIsPlaying(false);
    } else {
      // 재생
      audioElement?.play().catch((error) => {
        console.error('오디오 재생 실패:', error);
        setIsPlaying(false);
      });
      setIsPlaying(true);
    }
  };

  const handleDownload = () => {
    if (result?.audio_file_path) {
      // 실제 다운로드 로직 구현 필요
      const link = document.createElement('a');
      link.href = result.audio_file_path;
      link.download = `podcast_${result.field.replace(/\s+/g, '_')}.mp3`;
      link.click();
    }
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // 모의 논문 데이터 (실제로는 논문 선택 UI에서 가져옴)
  const mockPapers = [
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
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <MicIcon sx={{ mr: 2, fontSize: 40, color: 'primary.main' }} />
        <Typography variant="h4" component="h1" sx={{ flexGrow: 1 }}>
          Daily Paper Podcast
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Home />}
          onClick={handleGoHome}
        >
          홈으로
        </Button>
      </Box>

      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          팟캐스트 생성
        </Typography>
        
        <Box sx={{ mb: 3 }}>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>분야 선택</InputLabel>
            <Select
              value={field}
              label="분야 선택"
              onChange={(e) => setField(e.target.value)}
            >
              {availableFields.map((f) => (
                <MenuItem key={f} value={f}>
                  {f}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            선택된 분야: {field}
          </Typography>

          <Button
            variant="contained"
            startIcon={<PodcastIcon />}
            onClick={handleGeneratePodcast}
            disabled={loading}
            fullWidth
            sx={{ mb: 2 }}
          >
            {loading ? (
              <>
                <CircularProgress size={20} sx={{ mr: 1 }} />
                팟캐스트 생성 중...
              </>
            ) : (
              '팟캐스트 생성'
            )}
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
      </Paper>

      {result && (
        <Paper elevation={3} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            생성된 팟캐스트
          </Typography>
          
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              분야: {result.field}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              생성 시간: {new Date(result.created_at).toLocaleString()}
            </Typography>
            {result.duration_seconds && (
              <Typography variant="body2" color="text.secondary">
                재생 시간: {formatDuration(result.duration_seconds)}
              </Typography>
            )}
          </Box>

          <Box sx={{ mb: 3 }}>
            <Button
              variant="outlined"
              startIcon={isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
              onClick={handlePlayPause}
              sx={{ mr: 2 }}
            >
              {isPlaying ? '일시정지' : '재생'}
            </Button>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={handleDownload}
              disabled={!result.audio_file_path}
            >
              다운로드
            </Button>
          </Box>

          <Divider sx={{ my: 2 }} />

          <Typography variant="h6" gutterBottom>
            분석된 논문들
          </Typography>
          <List>
            {result.papers.map((paper, index) => (
              <ListItem key={index} sx={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                <ListItemText
                  primary={paper.title}
                  secondary={`저자: ${paper.authors.join(', ')}`}
                />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  {paper.abstract.substring(0, 200)}...
                </Typography>
              </ListItem>
            ))}
          </List>

          <Divider sx={{ my: 2 }} />

          <Typography variant="h6" gutterBottom>
            분석 결과
          </Typography>
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
                {result.analysis_text}
              </Typography>
            </CardContent>
          </Card>
        </Paper>
      )}

      {/* 설명 섹션 */}
      <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          사용 방법
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          1. 원하는 AI 분야를 선택하세요
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          2. "팟캐스트 생성" 버튼을 클릭하세요
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          3. 시스템이 해당 분야의 랜덤 논문들을 분석하여 팟캐스트를 생성합니다
        </Typography>
        <Typography variant="body2" color="text.secondary">
          4. 생성된 분석 결과를 확인하고 오디오 파일을 다운로드할 수 있습니다
        </Typography>
      </Paper>
    </Container>
  );
};

export default PodcastPage; 