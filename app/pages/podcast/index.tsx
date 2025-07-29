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
  Dialog,
  DialogTitle,
  DialogContent,
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
import { analyzePaper, generateTTS, getPodcastAnalysis, getAvailableFields } from '../../api/podcast';
import AudioPlayer from '../../components/AudioPlayer';

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
  const [ttsLoading, setTtsLoading] = useState(false);
  const [result, setResult] = useState<PodcastResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [availableFields, setAvailableFields] = useState<string[]>([
    'Natural Language Processing (NLP)',
    'Computer Vision (CV)',
    'Multimodal',
    'Machine Learning / Deep Learning (ML/DL)'
  ]);
  const [audioDialogOpen, setAudioDialogOpen] = useState(false);
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

  const handleAnalyzePaper = async () => {
    setLoading(true);
    setError(null);

    try {
      // 논문 분석만 수행
      const response = await analyzePaper(field, []);
      
      if (response.success) {
        // 분석 완료까지 대기
        setTimeout(async () => {
          try {
            const analysisResult = await getPodcastAnalysis(response.analysis_id);
            setResult(analysisResult);
          } catch (err) {
            setError('분석 결과를 가져오는데 실패했습니다.');
          }
        }, 3000); // 3초 후 결과 조회
      } else {
        setError('논문 분석에 실패했습니다.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateTTS = async () => {
    if (!result) return;
    
    setTtsLoading(true);
    setError(null);

    try {
      // TTS 대본 및 오디오 생성
      const response = await generateTTS(result.id);
      
      if (response.success) {
        // TTS 생성 완료까지 대기
        setTimeout(async () => {
          try {
            const updatedResult = await getPodcastAnalysis(result.id);
            console.log('TTS 생성 후 결과:', updatedResult);
            console.log('오디오 파일 경로:', updatedResult.audio_file_path);
            setResult(updatedResult);
          } catch (err) {
            setError('TTS 결과를 가져오는데 실패했습니다.');
          }
        }, 5000); // 5초 후 결과 조회
      } else {
        setError('TTS 생성에 실패했습니다.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
    } finally {
      setTtsLoading(false);
    }
  };

  const handlePlayAudio = () => {
    if (!result?.audio_file_path) {
      console.error('오디오 파일 경로가 없습니다.');
      return;
    }
    setAudioDialogOpen(true);
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
            onClick={handleAnalyzePaper}
            disabled={loading}
            fullWidth
            sx={{ mb: 2 }}
          >
            {loading ? (
              <>
                <CircularProgress size={20} sx={{ mr: 1 }} />
                논문 분석 중...
              </>
            ) : (
              '논문 분석'
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
            {result.duration_seconds && result.duration_seconds > 0 && (
              <Typography variant="body2" color="text.secondary">
                재생 시간: {formatDuration(result.duration_seconds)}
              </Typography>
            )}
          </Box>

          <Box sx={{ mb: 3 }}>
            {!result.audio_file_path || result.audio_file_path === "" ? (
              <Button
                variant="contained"
                startIcon={<MicIcon />}
                onClick={handleGenerateTTS}
                disabled={ttsLoading}
                sx={{ mr: 2 }}
              >
                {ttsLoading ? (
                  <>
                    <CircularProgress size={20} sx={{ mr: 1 }} />
                    TTS 생성 중...
                  </>
                ) : (
                  'TTS 생성'
                )}
              </Button>
            ) : (
              <>
                <Button
                  variant="outlined"
                  startIcon={<PlayArrowIcon />}
                  onClick={handlePlayAudio}
                  sx={{ mr: 2 }}
                >
                  재생
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={handleDownload}
                  disabled={!result.audio_file_path}
                >
                  다운로드
                </Button>
              </>
            )}
          </Box>

          <Divider sx={{ my: 2 }} />

          <Typography variant="h6" gutterBottom>
            분석된 논문
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
              <Box sx={{ 
                '& h1, & h2, & h3, & h4, & h5, & h6': {
                  color: 'primary.main',
                  fontWeight: 600,
                  mb: 2,
                  mt: 3
                },
                '& h1': { fontSize: '1.8rem' },
                '& h2': { fontSize: '1.6rem' },
                '& h3': { fontSize: '1.4rem' },
                '& h4': { fontSize: '1.2rem' },
                '& h5': { fontSize: '1.1rem' },
                '& h6': { fontSize: '1rem' },
                '& p': { mb: 2, lineHeight: 1.6 },
                '& ul, & ol': { mb: 2, pl: 3 },
                '& li': { mb: 1 },
                '& strong': { fontWeight: 600 },
                '& em': { fontStyle: 'italic' },
                '& code': { 
                  backgroundColor: 'grey.100', 
                  padding: '2px 4px', 
                  borderRadius: 1,
                  fontFamily: 'monospace'
                },
                '& pre': { 
                  backgroundColor: 'grey.100', 
                  padding: 2, 
                  borderRadius: 1,
                  overflow: 'auto'
                },
                '& blockquote': {
                  borderLeft: '4px solid',
                  borderColor: 'primary.main',
                  pl: 2,
                  ml: 0,
                  fontStyle: 'italic',
                  color: 'text.secondary'
                }
              }}>
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {result.analysis_text}
                </ReactMarkdown>
              </Box>
            </CardContent>
          </Card>
        </Paper>
      )}

      {/* 오디오 플레이어 다이얼로그 */}
      <Dialog
        open={audioDialogOpen}
        onClose={() => setAudioDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          팟캐스트 재생
        </DialogTitle>
        <DialogContent>
          {result && (
            <AudioPlayer
              audioUrl={result.audio_file_path}
              title={`${result.field} - 팟캐스트`}
              onClose={() => setAudioDialogOpen(false)}
            />
          )}
        </DialogContent>
      </Dialog>

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