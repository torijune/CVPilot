import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
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
  List,
  ListItem,
  ListItemText,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  Grid,
  CardActionArea,
  Badge,
  Stepper,
  Step,
  StepLabel,
  StepContent,
} from '@mui/material';
import {
  Podcasts as PodcastIcon,
  PlayArrow as PlayArrowIcon,
  Download as DownloadIcon,
  Home,
  Mic as MicIcon,
  Warning as WarningIcon,
  Settings as SettingsIcon,
  School as SchoolIcon,
  Article as ArticleIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  ArrowForward as ArrowForwardIcon,
} from '@mui/icons-material';
import { useRouter } from 'next/router';
import { 
  analyzePaper, 
  generateTTS, 
  getPodcastAnalysis, 
  getAvailableFields,
  getConferencesByField,
  getPaperPreview,
  reselectPaper,
  ConferenceInfo,
  PaperPreviewResponse
} from '../../api/podcast';
import AudioPlayer from '../../components/AudioPlayer';

interface PodcastResult {
  id: string;
  field: string;
  papers: Array<{
    id: string;
    title: string;
    abstract: string;
    authors: string[];
    conference?: string;
    year?: number;
    url?: string;
  }>;
  analysis_text: string;
  audio_file_path: string;
  duration_seconds: number;
  created_at: string;
}

const steps = ['분야 선택', '학회 선택', '논문 확인', '분석 완료'];

const PodcastPage: React.FC = () => {
  // 스텝 관리
  const [activeStep, setActiveStep] = useState(0);
  
  // 선택된 데이터
  const [field, setField] = useState('');
  const [selectedConference, setSelectedConference] = useState<ConferenceInfo | null>(null);
  const [paperPreview, setPaperPreview] = useState<PaperPreviewResponse | null>(null);
  
  // 로딩 상태
  const [loading, setLoading] = useState(false);
  const [ttsLoading, setTtsLoading] = useState(false);
  const [reselectLoading, setReselectLoading] = useState(false);
  
  // 데이터
  const [availableFields, setAvailableFields] = useState<string[]>([]);
  const [conferences, setConferences] = useState<ConferenceInfo[]>([]);
  const [result, setResult] = useState<PodcastResult | null>(null);
  
  // UI 상태
  const [error, setError] = useState<string | null>(null);
  const [audioDialogOpen, setAudioDialogOpen] = useState(false);
  const [showTtsSettings, setShowTtsSettings] = useState(false);
  const [ttsSettings, setTtsSettings] = useState({
    voice: 'ko-KR-Neural2-A',
    speed: 0.9,
    gender: 'FEMALE'
  });
  
  const router = useRouter();

  // 분야 목록 로드
  useEffect(() => {
    const loadFields = async () => {
      try {
        const response = await getAvailableFields();
        if (response.fields && response.fields.length > 0) {
          setAvailableFields(response.fields);
        }
      } catch (err) {
        console.error('분야 목록 로드 실패:', err);
        setAvailableFields([
          'Natural Language Processing (NLP)',
          'Computer Vision (CV)',
          'Multimodal',
          'Machine Learning / Deep Learning (ML/DL)'
        ]);
      }
    };
    loadFields();
  }, []);

  // 분야 선택 핸들러
  const handleFieldSelect = async (selectedField: string) => {
    setField(selectedField);
    setLoading(true);
    setError(null);
    
    try {
      const response = await getConferencesByField(selectedField);
      setConferences(response.conferences);
      setActiveStep(1);
    } catch (err) {
      setError('학회 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 학회 선택 핸들러
  const handleConferenceSelect = async (conference: ConferenceInfo) => {
    setSelectedConference(conference);
    setLoading(true);
    setError(null);
    
    try {
      const response = await getPaperPreview(field, conference.name);
      setPaperPreview(response);
      setActiveStep(2);
    } catch (err) {
      setError('논문 미리보기를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 논문 재선택 핸들러
  const handleReselectPaper = async () => {
    if (!selectedConference || !paperPreview) return;
    
    setReselectLoading(true);
    setError(null);
    
    try {
      const response = await reselectPaper(field, selectedConference.name, paperPreview.paper.id);
      setPaperPreview(response);
    } catch (err) {
      setError('논문 재선택에 실패했습니다.');
    } finally {
      setReselectLoading(false);
    }
  };

  // 논문 분석 시작 핸들러
  const handleStartAnalysis = async () => {
    if (!paperPreview) return;
    
    setLoading(true);
    setError(null);

    try {
      // 선택된 논문으로 분석 요청
      const response = await analyzePaper(field, [paperPreview.paper]);
      
      if (response.success) {
        // 분석 완료까지 대기
        setTimeout(async () => {
          try {
            const analysisResult = await getPodcastAnalysis(response.analysis_id);
            setResult(analysisResult);
            setActiveStep(3);
          } catch (err) {
            setError('분석 결과를 가져오는데 실패했습니다.');
          }
        }, 3000);
      } else {
        setError('논문 분석에 실패했습니다.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // TTS 생성 핸들러
  const handleGenerateTTS = async () => {
    if (!result) return;
    
    setTtsLoading(true);
    setError(null);

    try {
      const response = await generateTTS(result.id, ttsSettings);
      
      if (response.success) {
        setTimeout(async () => {
          try {
            const updatedResult = await getPodcastAnalysis(result.id);
            setResult(updatedResult);
          } catch (err) {
            setError('TTS 결과를 가져오는데 실패했습니다.');
          }
        }, 5000);
      } else {
        setError('TTS 생성에 실패했습니다.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
    } finally {
      setTtsLoading(false);
    }
  };

  // 다시 시작 핸들러
  const handleRestart = () => {
    setActiveStep(0);
    setField('');
    setSelectedConference(null);
    setPaperPreview(null);
    setResult(null);
    setError(null);
    setConferences([]);
  };

  const handleGoHome = () => {
    router.push('/');
  };

  const handlePlayAudio = () => {
    if (!result?.audio_file_path) return;
    setAudioDialogOpen(true);
  };

  const handleDownload = () => {
    if (result?.audio_file_path) {
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

      {/* 진행 단계 */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Stepper activeStep={activeStep} orientation="horizontal">
          {steps.map((label, index) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* 단계별 컨텐츠 */}
             {activeStep === 0 && (
         <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
             1. 관심 분야를 선택해주세요
           </Typography>
           <Grid container spacing={2}>
             {availableFields.map((fieldOption) => (
               <Grid item xs={12} sm={6} md={4} key={fieldOption}>
                 <Card>
                   <CardActionArea onClick={() => handleFieldSelect(fieldOption)} disabled={loading}>
                     <CardContent>
                       <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                         <SchoolIcon sx={{ mr: 1, color: 'primary.main' }} />
                         <Typography variant="h6" component="div">
                           {fieldOption.split(' (')[0]}
                         </Typography>
                       </Box>
                       <Typography variant="body2" color="text.secondary">
                         {fieldOption}
        </Typography>
                     </CardContent>
                   </CardActionArea>
                 </Card>
               </Grid>
             ))}
           </Grid>
           {loading && (
             <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
               <CircularProgress />
             </Box>
           )}
           
           <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
             <Button
               variant="text"
               onClick={handleGoHome}
               startIcon={<Home />}
             >
               홈으로 돌아가기
             </Button>
           </Box>
         </Paper>
       )}

             {activeStep === 1 && (
         <Paper elevation={3} sx={{ p: 3 }}>
           <Typography variant="h6" gutterBottom>
             2. 학회를 선택해주세요
           </Typography>
           <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
             선택된 분야: {field}
           </Typography>
           <Grid container spacing={2}>
             {conferences.map((conference) => (
               <Grid item xs={12} sm={6} md={4} key={conference.name}>
                 <Card>
                   <CardActionArea onClick={() => handleConferenceSelect(conference)} disabled={loading}>
                     <CardContent>
                       <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                         <Badge badgeContent={conference.paper_count} color="primary" max={9999}>
                           <SchoolIcon sx={{ mr: 1, color: 'primary.main' }} />
                         </Badge>
                         <Typography variant="h6" component="div" sx={{ ml: 1 }}>
                           {conference.name.split(' (')[0]}
                         </Typography>
                       </Box>
                       <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                         논문 수: {conference.paper_count}개
                       </Typography>
                       <Typography variant="body2" color="text.secondary">
                         연도: {conference.year_range} (최신: {conference.latest_year})
                       </Typography>
                     </CardContent>
                   </CardActionArea>
                 </Card>
               </Grid>
              ))}
           </Grid>
           {loading && (
             <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
               <CircularProgress />
             </Box>
           )}
           
           <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
             <Button
               variant="text"
               onClick={() => setActiveStep(0)}
               startIcon={<ArrowForwardIcon sx={{ transform: 'rotate(180deg)' }} />}
             >
               분야 다시 선택
             </Button>
           </Box>
         </Paper>
       )}

      {activeStep === 2 && paperPreview && (
        <Paper elevation={3} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            3. 선택된 논문을 확인해주세요
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            분야: {field} | 학회: {selectedConference?.name.split(' (')[0]}
          </Typography>

          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                <ArticleIcon sx={{ mr: 1, color: 'primary.main', mt: 0.5 }} />
                <Box sx={{ flex: 1 }}>
                  <Typography variant="h6" component="div" sx={{ mb: 1 }}>
                    {paperPreview.paper.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    저자: {paperPreview.paper.authors.join(', ')}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {paperPreview.paper.conference} ({paperPreview.paper.year})
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    {paperPreview.paper.abstract}
                  </Typography>
                  {paperPreview.paper.url && (
                    <Button
                      size="small"
                      variant="outlined"
                      href={paperPreview.paper.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      원문 보기
                    </Button>
                  )}
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button
            variant="contained"
              startIcon={<CheckCircleIcon />}
              onClick={handleStartAnalysis}
            disabled={loading}
          >
            {loading ? (
              <>
                <CircularProgress size={20} sx={{ mr: 1 }} />
                  분석 중...
                </>
              ) : (
                '이 논문으로 분석하기'
              )}
            </Button>
            
            {paperPreview.can_reselect && (
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={handleReselectPaper}
                disabled={reselectLoading}
              >
                {reselectLoading ? (
                  <>
                    <CircularProgress size={20} sx={{ mr: 1 }} />
                    재선택 중...
              </>
            ) : (
                  '다른 논문 보기'
            )}
              </Button>
            )}
            
                         <Button
               variant="text"
               onClick={() => setActiveStep(1)}
             >
               학회 다시 선택
             </Button>
             <Button
               variant="text"
               onClick={() => setActiveStep(0)}
             >
               분야 다시 선택
          </Button>
        </Box>

          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            이 학회에는 총 {paperPreview.total_papers_in_conference}개의 논문이 있습니다.
          </Typography>
        </Paper>
      )}

      {activeStep === 3 && result && (
        <>
          <Paper elevation={1} sx={{ p: 2, mb: 2, bgcolor: '#fff5f5' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <WarningIcon sx={{ color: '#d32f2f' }} />
              <Typography variant="body2" color="#d32f2f">
                해당 분석 및 팟캐스트는 각 논문의 초록(abstract)만 읽고 AI가 요약한 것입니다. 
                더 자세하고 정확한 정보는 논문 원문을 참고해주세요.
              </Typography>
            </Box>
          </Paper>

          <Paper elevation={3} sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
              생성된 팟캐스트
            </Typography>
              <Button
                variant="outlined"
                onClick={handleRestart}
                startIcon={<RefreshIcon />}
              >
                다시 시작
              </Button>
            </Box>
          
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

            {/* TTS 설정 UI */}
            {showTtsSettings && (
              <Paper elevation={2} sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
                <Typography variant="h6" gutterBottom>
                  TTS 설정
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <FormControl sx={{ minWidth: 200 }}>
                    <InputLabel>음성 선택</InputLabel>
                    <Select
                      value={ttsSettings.voice}
                      label="음성 선택"
                      onChange={(e) => setTtsSettings({...ttsSettings, voice: e.target.value})}
                    >
                      <MenuItem value="ko-KR-Neural2-A">여성 음성 A</MenuItem>
                      <MenuItem value="ko-KR-Neural2-B">여성 음성 B</MenuItem>
                      <MenuItem value="ko-KR-Neural2-C">남성 음성 C</MenuItem>
                      <MenuItem value="ko-KR-Neural2-D">남성 음성 D</MenuItem>
                    </Select>
                  </FormControl>
                  
                  <FormControl sx={{ minWidth: 150 }}>
                    <InputLabel>속도</InputLabel>
                    <Select
                      value={ttsSettings.speed}
                      label="속도"
                      onChange={(e) => setTtsSettings({...ttsSettings, speed: e.target.value})}
                    >
                      <MenuItem value={0.5}>매우 느림</MenuItem>
                      <MenuItem value={0.7}>느림</MenuItem>
                      <MenuItem value={0.9}>보통</MenuItem>
                      <MenuItem value={1.1}>빠름</MenuItem>
                      <MenuItem value={1.3}>매우 빠름</MenuItem>
                    </Select>
                  </FormControl>
                  
                  <FormControl sx={{ minWidth: 120 }}>
                    <InputLabel>성별</InputLabel>
                    <Select
                      value={ttsSettings.gender}
                      label="성별"
                      onChange={(e) => setTtsSettings({...ttsSettings, gender: e.target.value})}
                    >
                      <MenuItem value="FEMALE">여성</MenuItem>
                      <MenuItem value="MALE">남성</MenuItem>
                      <MenuItem value="NEUTRAL">중성</MenuItem>
                    </Select>
                  </FormControl>
                </Box>
              </Paper>
            )}

          <Box sx={{ mb: 3 }}>
            {!result.audio_file_path || result.audio_file_path === "" ? (
              <>
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
                <Button
                  variant="outlined"
                  startIcon={<SettingsIcon />}
                  onClick={() => setShowTtsSettings(!showTtsSettings)}
                >
                  TTS 설정
                </Button>
              </>
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
                  {paper.url && (
                    <Button
                      size="small"
                      variant="outlined"
                      href={paper.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      sx={{ mt: 1 }}
                    >
                      원문 보기
                    </Button>
                  )}
              </ListItem>
            ))}
          </List>

          <Divider sx={{ my: 2 }} />

          <Typography variant="h6" gutterBottom>
            분석 결과
          </Typography>
          <Box sx={{ 
            '& h1, & h2, & h3, & h4, & h5, & h6': {
              color: 'primary.main',
              fontWeight: 600,
              mb: 1,
              mt: 2
            },
            '& h1': { fontSize: '1.5rem' },
            '& h2': { fontSize: '1.3rem' },
            '& h3': { fontSize: '1.2rem' },
            '& h4': { fontSize: '1.1rem' },
            '& h5': { fontSize: '1rem' },
            '& h6': { fontSize: '1rem' },
            '& p': { 
              mb: 1, 
              lineHeight: 1.5
            },
            '& ul, & ol': { 
              mb: 1, 
              pl: 2
            },
            '& li': { 
              mb: 0.5
            },
            '& strong': { fontWeight: 600 },
            '& em': { fontStyle: 'italic' },
            '& code': { 
              backgroundColor: 'grey.100', 
              padding: '1px 3px', 
              borderRadius: 1,
              fontFamily: 'monospace'
            },
            '& pre': { 
              backgroundColor: 'grey.100', 
              padding: 1, 
              borderRadius: 1,
              overflow: 'auto'
            },
            '& blockquote': {
              borderLeft: '3px solid',
              borderColor: 'primary.main',
              pl: 1,
              ml: 0,
              fontStyle: 'italic',
              color: 'text.secondary'
            },
            '& a': {
              color: 'primary.main',
              textDecoration: 'none',
              '&:hover': {
                textDecoration: 'underline'
              }
            }
          }}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {result.analysis_text}
            </ReactMarkdown>
          </Box>
        </Paper>
        </>
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

      {/* 사용 방법 */}
      <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          새로운 사용 방법
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          1. 원하는 AI 분야를 선택하세요
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          2. 해당 분야의 학회 목록에서 관심있는 학회를 선택하세요
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          3. 랜덤으로 선택된 논문을 확인하고, 마음에 들지 않으면 다른 논문을 선택하세요
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          4. 마음에 드는 논문을 찾았다면 분석을 시작하세요
        </Typography>
        <Typography variant="body2" color="text.secondary">
          5. 생성된 분석 결과를 확인하고 TTS로 음성 파일을 생성할 수 있습니다
        </Typography>
      </Paper>
    </Container>
  );
};

export default PodcastPage; 