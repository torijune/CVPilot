import React, { useState, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  CircularProgress,
  Alert,
  Avatar,
  Container,
  Stepper,
  Step,
  StepLabel
} from '@mui/material';
import {
  QuestionAnswer as QuestionAnswerIcon,
  Send as SendIcon,
  Person as PersonIcon,
  SmartToy as SmartToyIcon,
  Home,
  Upload as UploadIcon,
  Description as DescriptionIcon,
  Refresh as RefreshIcon,
  PersonSearch as PersonSearchIcon,
  SelfImprovement as SelfImprovementIcon,
  Feedback as FeedbackIcon
} from '@mui/icons-material';
import { useRouter } from 'next/router';
import {
  uploadCV,
  createQASession,
  sendMessage,
  getNewInterviewQuestions,
  askSelectedQuestion,
  QAMessage,
  QASessionResponse,
  CVUploadResponse,
  QAMessageResponse
} from '../../api/cv-qa';

const steps = ['CV 업로드', '모드 선택', 'QA 세션'];

const CVQAPage: React.FC = () => {
  // 스텝 관리
  const [activeStep, setActiveStep] = useState(0);
  
  // CV 업로드 관련
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [analysisId, setAnalysisId] = useState('');
  const [uploadLoading, setUploadLoading] = useState(false);
  
  // 모드 선택
  const [selectedMode, setSelectedMode] = useState<'interview' | 'practice' | null>(null);
  
  // QA 세션 관련
  const [sessionId, setSessionId] = useState('');
  const [messages, setMessages] = useState<QAMessage[]>([]);
  const [userMessage, setUserMessage] = useState('');
  const [messageLoading, setMessageLoading] = useState(false);
  
  // Interview 모드 전용
  const [interviewQuestions, setInterviewQuestions] = useState<string[]>([]);
  const [showQuestionSelector, setShowQuestionSelector] = useState(false);
  const [generatingQuestions, setGeneratingQuestions] = useState(false);
  
  // 공통 상태
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // 메시지가 추가될 때마다 스크롤
  React.useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleGoHome = () => {
    router.push('/');
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setCvFile(file);
      setError(null);
    }
  };

  const handleUploadCV = async () => {
    if (!cvFile) {
      setError('CV 파일을 선택해주세요.');
      return;
    }

    setUploadLoading(true);
    setError(null);

    try {
      const result = await uploadCV(cvFile);
      setAnalysisId(result.analysis_id);
      setActiveStep(1); // 모드 선택 단계로 이동
    } catch (err) {
      setError(err instanceof Error ? err.message : 'CV 업로드 중 오류가 발생했습니다.');
    } finally {
      setUploadLoading(false);
    }
  };

  const handleModeSelect = async (mode: 'interview' | 'practice') => {
    setSelectedMode(mode);
    setError(null);

    try {
      const sessionResponse = await createQASession({
        analysis_id: analysisId,
        mode: mode
      });
      
      setSessionId(sessionResponse.session_id);
      
      // 환영 메시지 추가
      const welcomeMessage: QAMessage = {
        message_id: 'welcome',
            role: 'assistant',
        content: sessionResponse.message,
            timestamp: new Date().toISOString()
      };
      setMessages([welcomeMessage]);

      if (mode === 'interview' && sessionResponse.interview_questions) {
        setInterviewQuestions(sessionResponse.interview_questions);
        setShowQuestionSelector(true);
      }

      setActiveStep(2); // QA 세션 단계로 이동
    } catch (err) {
      setError(err instanceof Error ? err.message : 'QA 세션 생성 중 오류가 발생했습니다.');
    }
  };

  const handleSendMessage = async () => {
    if (!userMessage.trim() || !sessionId) return;

    const newUserMessage: QAMessage = {
      message_id: `msg-${Date.now()}`,
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    };

    // 사용자 메시지 추가
    setMessages(prev => [...prev, newUserMessage]);
    const currentMessage = userMessage;
    setUserMessage('');
    setMessageLoading(true);

    try {
      const response = await sendMessage(sessionId, { message: currentMessage });
      
      const aiMessage: QAMessage = {
        message_id: response.message_id,
          role: 'assistant',
        content: response.content,
        timestamp: response.timestamp || new Date().toISOString(),
        feedback: response.feedback,
        follow_up_question: response.follow_up_question
        };

      setMessages(prev => [...prev, aiMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : '메시지 전송 중 오류가 발생했습니다.');
    } finally {
      setMessageLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleQuestionSelect = async (question: string) => {
    if (!sessionId) return;

    setShowQuestionSelector(false);
    setMessageLoading(true);

    try {
      // 백엔드에 질문 전송하여 AI가 사용자에게 물어보도록 함
      const response = await askSelectedQuestion(sessionId, question);
      
      // AI가 질문하는 메시지 추가
      const aiQuestionMessage: QAMessage = {
        message_id: response.message_id,
        role: 'assistant',
        content: response.content,
        timestamp: response.timestamp || new Date().toISOString()
      };

      setMessages(prev => [...prev, aiQuestionMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : '질문 전송 중 오류가 발생했습니다.');
    } finally {
      setMessageLoading(false);
    }
  };

  const handleGetNewQuestions = async () => {
    if (!sessionId) return;

    setGeneratingQuestions(true);
    setError(null);

    try {
      const response = await getNewInterviewQuestions(sessionId);
      setInterviewQuestions(response.questions);
      setShowQuestionSelector(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : '새로운 질문 생성 중 오류가 발생했습니다.');
    } finally {
      setGeneratingQuestions(false);
    }
  };

  const handleRestart = () => {
    setActiveStep(0);
    setCvFile(null);
    setAnalysisId('');
    setSelectedMode(null);
    setSessionId('');
    setMessages([]);
    setUserMessage('');
    setInterviewQuestions([]);
    setShowQuestionSelector(false);
    setError(null);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <QuestionAnswerIcon sx={{ mr: 2, fontSize: 40, color: 'primary.main' }} />
        <Typography variant="h4" component="h1" sx={{ flexGrow: 1 }}>
          CV 면접 QA
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
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom>
            1. CV 파일을 업로드해주세요
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            PDF, DOCX, TXT 파일을 지원합니다.
          </Typography>

          <Box sx={{ mb: 3 }}>
            <input
              accept=".pdf,.docx,.txt"
              style={{ display: 'none' }}
              id="cv-file-input"
              type="file"
              onChange={handleFileUpload}
            />
            <label htmlFor="cv-file-input">
              <Button
                variant="outlined"
                component="span"
                startIcon={<DescriptionIcon />}
                size="large"
                sx={{ mr: 2 }}
              >
                파일 선택
              </Button>
            </label>

            {cvFile && (
              <Typography variant="body2" sx={{ mt: 1 }}>
                선택된 파일: {cvFile.name}
              </Typography>
            )}
          </Box>

          <Button
            variant="contained"
            size="large"
            onClick={handleUploadCV}
            disabled={uploadLoading || !cvFile}
            startIcon={uploadLoading ? <CircularProgress size={20} /> : <UploadIcon />}
          >
            {uploadLoading ? '업로드 중...' : 'CV 업로드 및 분석'}
          </Button>
        </Paper>
      )}

      {activeStep === 1 && (
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom>
            2. 원하는 모드를 선택해주세요
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            두 가지 모드 중 하나를 선택하여 면접 연습을 시작하세요.
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card sx={{ height: '100%' }}>
                <CardActionArea 
                  onClick={() => handleModeSelect('interview')}
                  sx={{ height: '100%', p: 3 }}
                >
                  <CardContent sx={{ textAlign: 'center' }}>
                    <PersonSearchIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
                    <Typography variant="h6" component="div" sx={{ mb: 2 }}>
                      면접관 모드
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      AI가 면접관이 되어 CV를 바탕으로 질문을 던집니다.
                    </Typography>
                    <Box component="ul" sx={{ textAlign: 'left', pl: 2 }}>
                      <li>CV 기반 맞춤형 질문 제공</li>
                      <li>답변에 대한 피드백</li>
                      <li>꼬리 질문으로 심화 탐구</li>
                      <li>실제 면접과 유사한 경험</li>
        </Box>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card sx={{ height: '100%' }}>
                <CardActionArea 
                  onClick={() => handleModeSelect('practice')}
                  sx={{ height: '100%', p: 3 }}
                >
                  <CardContent sx={{ textAlign: 'center' }}>
                    <SelfImprovementIcon sx={{ fontSize: 60, color: 'secondary.main', mb: 2 }} />
                    <Typography variant="h6" component="div" sx={{ mb: 2 }}>
                      연습 모드
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      예상 질문을 미리 연습하고 모범 답변을 확인하세요.
                    </Typography>
                    <Box component="ul" sx={{ textAlign: 'left', pl: 2 }}>
                      <li>자유로운 질문 입력</li>
                      <li>CV 기반 모범 답변 예시</li>
                      <li>답변 전략과 팁 제공</li>
                      <li>면접 준비를 위한 조언</li>
                    </Box>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          </Grid>
        </Paper>
      )}

      {activeStep === 2 && (
        <Box>
          {/* 사용 방법 안내 - 대화창 위에 배치 */}
          <Paper elevation={2} sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
            <Typography variant="h6" gutterBottom>
              사용 방법
                </Typography>
            <Box component="ol" sx={{ pl: 2, m: 0 }}>
              <li>CV 파일을 업로드하여 분석을 시작합니다.</li>
              <li>원하는 모드를 선택합니다:
                <ul>
                  <li><strong>면접관 모드</strong>: AI가 면접관이 되어 질문하고 피드백을 제공</li>
                  <li><strong>연습 모드</strong>: 예상 질문을 입력하여 모범 답변과 조언을 받음</li>
                </ul>
              </li>
              <li>실시간 채팅으로 면접 연습을 진행합니다.</li>
              <li>피드백을 통해 답변을 개선해나갑니다.</li>
            </Box>
          </Paper>

          {/* 면접 질문 선택 UI (Interview 모드) */}
          {selectedMode === 'interview' && showQuestionSelector && interviewQuestions.length > 0 && (
            <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                면접 질문 선택
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                CV를 분석해서 생성된 맞춤형 질문입니다. 선택하거나 직접 질문을 입력하세요.
              </Typography>
              <Grid container spacing={2}>
                {interviewQuestions.map((question, index) => (
                  <Grid item xs={12} key={index}>
                    <Button
                      variant="outlined"
                  fullWidth
                      onClick={() => handleQuestionSelect(question)}
                      sx={{
                        justifyContent: 'flex-start',
                        textAlign: 'left',
                        py: 2,
                        px: 3,
                        '&:hover': {
                          bgcolor: 'primary.50'
                        }
                      }}
                    >
                      <Typography variant="body2">
                        {question}
                      </Typography>
                    </Button>
                  </Grid>
                ))}
              </Grid>
              <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'center' }}>
                <Button
                  variant="text"
                  onClick={() => setShowQuestionSelector(false)}
                >
                  직접 질문 입력
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={handleGetNewQuestions}
                  disabled={generatingQuestions}
                >
                  {generatingQuestions ? '생성 중...' : '새로운 질문'}
                </Button>
              </Box>
            </Paper>
          )}

          {/* 채팅 영역 - 전체 화면 높이로 설정 */}
          <Paper elevation={3} sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
            {/* 헤더 */}
            <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider', bgcolor: 'grey.50' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  {selectedMode === 'interview' ? (
                    <PersonSearchIcon sx={{ mr: 1, color: 'primary.main' }} />
                  ) : (
                    <SelfImprovementIcon sx={{ mr: 1, color: 'secondary.main' }} />
                  )}
                  <Typography variant="h6">
                    {selectedMode === 'interview' ? '면접관 모드' : '연습 모드'}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  {selectedMode === 'interview' && (
                    <Button
                      size="small"
                      variant="outlined"
                      startIcon={<RefreshIcon />}
                      onClick={() => setShowQuestionSelector(true)}
                    >
                      질문 선택
                    </Button>
                  )}
                  <Button
                    size="small"
                    variant="text"
                    onClick={handleRestart}
                  >
                    다시 시작
                  </Button>
                </Box>
              </Box>
                </Box>

                {/* 메시지 영역 */}
                <Box sx={{ 
                  flex: 1, 
                  overflow: 'auto', 
              p: 2,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 2
                }}>
              {messages.map((message) => (
                    <Box
                  key={message.message_id}
                      sx={{
                        display: 'flex',
                        justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                    mb: 1
                      }}
                    >
                      <Box sx={{
                    maxWidth: '80%',
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: 1
                      }}>
                        {message.role === 'assistant' && (
                      <Avatar sx={{ 
                        bgcolor: selectedMode === 'interview' ? 'primary.main' : 'secondary.main', 
                        width: 32, 
                        height: 32 
                      }}>
                        <SmartToyIcon fontSize="small" />
                          </Avatar>
                        )}
                        
                    <Box>
                      <Paper
                        elevation={1}
                        sx={{
                          p: 2,
                          bgcolor: message.role === 'user' ? 'primary.main' : 'white',
                          color: message.role === 'user' ? 'white' : 'text.primary',
                          borderRadius: 2,
                          mb: 1
                        }}
                      >
                        {message.role === 'user' ? (
                          <Typography variant="body1">
                            {message.content}
                          </Typography>
                        ) : (
                          <Box sx={{ 
                            '& h1, & h2, & h3, & h4, & h5, & h6': { 
                              color: 'text.primary',
                              fontWeight: 600,
                              mb: 1,
                              mt: 2
                            },
                            '& p': { 
                              color: 'text.primary',
                              mb: 1
                            },
                            '& ul, & ol': { 
                              pl: 2,
                              mb: 1
                            },
                            '& li': { 
                              color: 'text.primary',
                              mb: 0.5
                            },
                            '& strong': { 
                              fontWeight: 600
                            },
                            '& em': { 
                              fontStyle: 'italic'
                            },
                            '& blockquote': { 
                              borderLeft: '4px solid',
                              borderColor: 'primary.main',
                              pl: 2,
                              ml: 0,
                              my: 1
                            },
                            '& code': { 
                              bgcolor: 'grey.100',
                              px: 0.5,
                              py: 0.25,
                              borderRadius: 0.5,
                              fontFamily: 'monospace'
                            }
                          }}>
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {message.content}
                            </ReactMarkdown>
                          </Box>
                        )}
                      </Paper>

                      {/* Interview 모드 피드백 */}
                      {message.feedback && (
                        <Paper
                          elevation={1}
                          sx={{
                            p: 2,
                            bgcolor: 'info.50',
                            borderRadius: 2,
                            mb: 1
                          }}
                        >
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                            <FeedbackIcon sx={{ mr: 1, color: 'info.main', fontSize: 'small' }} />
                            <Typography variant="subtitle2" color="info.main">
                              피드백
                            </Typography>
                          </Box>
                          <Typography variant="body2">
                            {message.feedback}
                          </Typography>
                        </Paper>
                      )}

                      {/* Interview 모드 꼬리 질문 */}
                      {message.follow_up_question && (
                        <Paper
                          elevation={1}
                          sx={{
                            p: 2,
                            bgcolor: 'warning.50',
                            borderRadius: 2
                          }}
                        >
                          <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                            💡 {message.follow_up_question}
                          </Typography>
                        </Paper>
                      )}
                    </Box>

                        {message.role === 'user' && (
                      <Avatar sx={{ bgcolor: 'grey.400', width: 32, height: 32 }}>
                        <PersonIcon fontSize="small" />
                          </Avatar>
                        )}
                      </Box>
                    </Box>
                  ))}

              {messageLoading && (
                <Box sx={{ display: 'flex', justifyContent: 'flex-start' }}>
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                    <Avatar sx={{ 
                      bgcolor: selectedMode === 'interview' ? 'primary.main' : 'secondary.main', 
                      width: 32, 
                      height: 32 
                    }}>
                      <SmartToyIcon fontSize="small" />
                        </Avatar>
                    <Paper elevation={1} sx={{ p: 2, borderRadius: 2 }}>
                          <CircularProgress size={20} />
                        </Paper>
                      </Box>
                    </Box>
                  )}
              <div ref={messagesEndRef} />
                </Box>

                {/* 메시지 입력 */}
                <Box sx={{ 
              p: 2, 
                  borderTop: '1px solid',
              borderColor: 'divider'
                }}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                    <TextField
                      fullWidth
                      multiline
                      rows={2}
                  placeholder={
                    selectedMode === 'interview' 
                      ? "면접관의 질문에 답변하세요..." 
                      : "연습하고 싶은 면접 질문을 입력하세요..."
                  }
                      value={userMessage}
                      onChange={(e) => setUserMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                  disabled={messageLoading}
                  variant="outlined"
                  size="small"
                    />
                    <Button
                      variant="contained"
                      onClick={handleSendMessage}
                  disabled={messageLoading || !userMessage.trim()}
                  sx={{ minWidth: 48, height: 'fit-content', alignSelf: 'flex-end' }}
                    >
                      <SendIcon />
                    </Button>
                  </Box>
                </Box>
              </Paper>
        </Box>
      )}


    </Container>
  );
};

export default CVQAPage; 