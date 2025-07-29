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
  Divider,
  Avatar
} from '@mui/material';
import {
  QuestionAnswer as QuestionAnswerIcon,
  Send as SendIcon,
  Person as PersonIcon,
  SmartToy as SmartToyIcon,
  Psychology as PsychologyIcon,
  Home
} from '@mui/icons-material';
import { useRouter } from 'next/router';

interface QAMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface QASession {
  id: string;
  cv_analysis_id: string;
  messages: QAMessage[];
  created_at: string;
}

const CVQAPage: React.FC = () => {
  const [cvAnalysisId, setCvAnalysisId] = useState('');
  const [userMessage, setUserMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [session, setSession] = useState<QASession | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleGoHome = () => {
    router.push('/');
  };

  const handleStartSession = async () => {
    if (!cvAnalysisId.trim()) {
      setError('CV 분석 ID를 입력해주세요.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // 실제로는 QA Session API를 호출
      // 현재는 모의 데이터 사용
      const mockSession: QASession = {
        id: 'qa-session-1',
        cv_analysis_id: cvAnalysisId,
        messages: [
          {
            id: 'msg-1',
            role: 'assistant',
            content: '안녕하세요! CV 기반 면접 질의응답을 도와드리겠습니다. 어떤 질문이든 편하게 해주세요.',
            timestamp: new Date().toISOString()
          }
        ],
        created_at: new Date().toISOString()
      };

      setSession(mockSession);
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!userMessage.trim() || !session) return;

    const newUserMessage: QAMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    };

    // 사용자 메시지 추가
    setSession(prev => prev ? {
      ...prev,
      messages: [...prev.messages, newUserMessage]
    } : null);

    setUserMessage('');
    setLoading(true);

    try {
      // 실제로는 AI 응답 API를 호출
      // 현재는 모의 응답 사용
      setTimeout(() => {
        const aiResponse: QAMessage = {
          id: `msg-${Date.now() + 1}`,
          role: 'assistant',
          content: `좋은 질문이네요! CV를 보니 ${userMessage}에 대한 경험이 있으시군요. 구체적으로 어떤 부분에 대해 더 알고 싶으신가요?`,
          timestamp: new Date().toISOString()
        };

        setSession(prev => prev ? {
          ...prev,
          messages: [...prev.messages, aiResponse]
        } : null);
        setLoading(false);
      }, 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : '메시지 전송 중 오류가 발생했습니다.');
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', py: 4 }}>
      <Box sx={{ maxWidth: 1200, mx: 'auto', px: 3 }}>
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
          
          <Typography variant="h3" sx={{ mb: 2, fontWeight: 700 }}>
            CV Q&A
          </Typography>
          <Typography variant="h6" color="text.secondary">
            CV에 대한 질문을 하고 AI의 답변을 받아보세요
          </Typography>
        </Box>

        {!session ? (
          // 세션 시작 화면
          <Grid container spacing={4} justifyContent="center">
            <Grid item xs={12} md={6}>
              <Paper elevation={0} sx={{ p: 4, textAlign: 'center' }}>
                <QuestionAnswerIcon sx={{ fontSize: 64, mb: 2, color: 'primary.main' }} />
                <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
                  QA 세션 시작
                </Typography>

                <TextField
                  fullWidth
                  label="CV 분석 ID"
                  value={cvAnalysisId}
                  onChange={(e) => setCvAnalysisId(e.target.value)}
                  placeholder="CV 분석에서 받은 ID를 입력하세요"
                  sx={{ mb: 3 }}
                />

                <Button
                  variant="contained"
                  fullWidth
                  size="large"
                  onClick={handleStartSession}
                  disabled={loading || !cvAnalysisId.trim()}
                  startIcon={loading ? <CircularProgress size={20} /> : <QuestionAnswerIcon />}
                  sx={{ py: 1.5 }}
                >
                  {loading ? '세션 시작 중...' : 'QA 세션 시작'}
                </Button>

                {error && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {error}
                  </Alert>
                )}
              </Paper>
            </Grid>
          </Grid>
        ) : (
          // 채팅 화면
          <Grid container spacing={4}>
            <Grid item xs={12} md={8}>
              <Paper elevation={0} sx={{ height: '70vh', display: 'flex', flexDirection: 'column' }}>
                {/* 채팅 헤더 */}
                <Box sx={{ 
                  p: 3, 
                  borderBottom: '1px solid',
                  borderColor: 'grey.200',
                  bgcolor: 'primary.main',
                  color: 'white'
                }}>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    CV 기반 면접 QA
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    세션 ID: {session.id}
                  </Typography>
                </Box>

                {/* 메시지 영역 */}
                <Box sx={{ 
                  flex: 1, 
                  overflow: 'auto', 
                  p: 3,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 2
                }}>
                  {session.messages.map((message) => (
                    <Box
                      key={message.id}
                      sx={{
                        display: 'flex',
                        justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                        mb: 2
                      }}
                    >
                      <Box sx={{
                        maxWidth: '70%',
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: 1
                      }}>
                        {message.role === 'assistant' && (
                          <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                            <SmartToyIcon />
                          </Avatar>
                        )}
                        
                        <Paper
                          elevation={1}
                          sx={{
                            p: 2,
                            bgcolor: message.role === 'user' ? 'primary.main' : 'grey.100',
                            color: message.role === 'user' ? 'white' : 'text.primary',
                            borderRadius: 2,
                            wordBreak: 'break-word'
                          }}
                        >
                          <Typography variant="body1">
                            {message.content}
                          </Typography>
                          <Typography variant="caption" sx={{ 
                            opacity: 0.7,
                            display: 'block',
                            mt: 1
                          }}>
                            {new Date(message.timestamp).toLocaleTimeString()}
                          </Typography>
                        </Paper>

                        {message.role === 'user' && (
                          <Avatar sx={{ bgcolor: 'secondary.main', width: 32, height: 32 }}>
                            <PersonIcon />
                          </Avatar>
                        )}
                      </Box>
                    </Box>
                  ))}

                  {loading && (
                    <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                        <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                          <SmartToyIcon />
                        </Avatar>
                        <Paper elevation={1} sx={{ p: 2, bgcolor: 'grey.100', borderRadius: 2 }}>
                          <CircularProgress size={20} />
                        </Paper>
                      </Box>
                    </Box>
                  )}
                </Box>

                {/* 메시지 입력 */}
                <Box sx={{ 
                  p: 3, 
                  borderTop: '1px solid',
                  borderColor: 'grey.200'
                }}>
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <TextField
                      fullWidth
                      multiline
                      rows={2}
                      placeholder="질문을 입력하세요..."
                      value={userMessage}
                      onChange={(e) => setUserMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      disabled={loading}
                    />
                    <Button
                      variant="contained"
                      onClick={handleSendMessage}
                      disabled={loading || !userMessage.trim()}
                      sx={{ minWidth: 56 }}
                    >
                      <SendIcon />
                    </Button>
                  </Box>
                </Box>
              </Paper>
            </Grid>

            {/* 사이드바 */}
            <Grid item xs={12} md={4}>
              <Paper elevation={0} sx={{ p: 3, height: 'fit-content' }}>
                <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                  면접 팁
                </Typography>
                
                <List>
                  {[
                    'CV에 있는 프로젝트에 대해 구체적으로 설명할 수 있도록 준비하세요',
                    '기술 스킬에 대한 깊이 있는 이해를 보여주세요',
                    '연구 경험이나 논문에 대해 자세히 설명할 수 있어야 합니다',
                    '약점에 대해서는 개선 계획을 함께 제시하세요',
                    '최신 기술 트렌드에 대한 관심을 보여주세요'
                  ].map((tip, index) => (
                    <ListItem key={index} sx={{ py: 1 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <PsychologyIcon color="primary" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText 
                        primary={tip}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </Paper>
            </Grid>
          </Grid>
        )}
      </Box>
    </Box>
  );
};

export default CVQAPage; 