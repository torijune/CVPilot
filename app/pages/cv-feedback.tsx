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
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Feedback as FeedbackIcon,
  Lightbulb as LightbulbIcon,
  School as SchoolIcon,
  Work as WorkIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Star as StarIcon
} from '@mui/icons-material';

interface FeedbackResult {
  id: string;
  cv_analysis_id: string;
  improvement_projects: Array<{
    title: string;
    description: string;
    technologies: string[];
    duration: string;
    difficulty: string;
    learning_outcomes: string[];
  }>;
  skill_recommendations: string[];
  career_path_suggestions: string[];
  created_at: string;
}

const CVFeedbackPage: React.FC = () => {
  const [cvAnalysisId, setCvAnalysisId] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<FeedbackResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGetFeedback = async () => {
    if (!cvAnalysisId.trim()) {
      setError('CV 분석 ID를 입력해주세요.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // 실제로는 CV Feedback API를 호출
      // 현재는 모의 데이터 사용
      const mockResult: FeedbackResult = {
        id: 'feedback-1',
        cv_analysis_id: cvAnalysisId,
        improvement_projects: [
          {
            title: '딥러닝 기반 이미지 분류 프로젝트',
            description: 'CNN과 Transformer를 활용한 이미지 분류 시스템 구축',
            technologies: ['Python', 'PyTorch', 'OpenCV', 'Docker'],
            duration: '3-4개월',
            difficulty: '중급',
            learning_outcomes: ['CNN 아키텍처 이해', '데이터 전처리', '모델 최적화']
          },
          {
            title: '자연어 처리 챗봇 개발',
            description: 'BERT 기반 대화형 챗봇 시스템 구현',
            technologies: ['Python', 'Transformers', 'FastAPI', 'PostgreSQL'],
            duration: '2-3개월',
            difficulty: '중급',
            learning_outcomes: ['NLP 기초', 'API 개발', '데이터베이스 설계']
          }
        ],
        skill_recommendations: [
          'Docker', 'Kubernetes', 'AWS', 'Git', 'CI/CD', 'MongoDB'
        ],
        career_path_suggestions: [
          '1. AI/ML 엔지니어로 발전',
          '2. 연구원으로 전향',
          '3. 데이터 사이언티스트로 전환',
          '4. 풀스택 개발자로 확장'
        ],
        created_at: new Date().toISOString()
      };

      setResult(mockResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', py: 4 }}>
      <Box sx={{ maxWidth: 1200, mx: 'auto', px: 3 }}>
        {/* 헤더 */}
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Typography variant="h3" sx={{ mb: 2, fontWeight: 700 }}>
            CV 피드백
          </Typography>
          <Typography variant="h6" color="text.secondary">
            AI가 제안하는 개선 프로젝트와 커리어 방향을 확인하세요
          </Typography>
        </Box>

        <Grid container spacing={4}>
          {/* 입력 섹션 */}
          <Grid item xs={12} md={4}>
            <Paper elevation={0} sx={{ p: 4, height: 'fit-content' }}>
              <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
                피드백 요청
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
                onClick={handleGetFeedback}
                disabled={loading || !cvAnalysisId.trim()}
                startIcon={loading ? <CircularProgress size={20} /> : <FeedbackIcon />}
                sx={{ py: 1.5 }}
              >
                {loading ? '피드백 생성 중...' : '피드백 받기'}
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
                {/* 개선 프로젝트 */}
                <Card sx={{ mb: 3 }}>
                  <CardContent>
                    <Typography variant="h5" sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
                      <LightbulbIcon sx={{ mr: 1, color: 'primary.main' }} />
                      추천 개선 프로젝트
                    </Typography>
                    
                    {result.improvement_projects.map((project, index) => (
                      <Accordion key={index} sx={{ mb: 2 }}>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                          <Typography variant="h6" sx={{ fontWeight: 600 }}>
                            {project.title}
                          </Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            {project.description}
                          </Typography>
                          
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                              사용 기술:
                            </Typography>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                              {project.technologies.map((tech, techIndex) => (
                                <Chip
                                  key={techIndex}
                                  label={tech}
                                  color="primary"
                                  variant="outlined"
                                  size="small"
                                />
                              ))}
                            </Box>
                          </Box>
                          
                          <Grid container spacing={2}>
                            <Grid item xs={6}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                                예상 기간: {project.duration}
                              </Typography>
                            </Grid>
                            <Grid item xs={6}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                                난이도: {project.difficulty}
                              </Typography>
                            </Grid>
                          </Grid>
                          
                          <Box sx={{ mt: 2 }}>
                            <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                              학습 목표:
                            </Typography>
                            <List dense>
                              {project.learning_outcomes.map((outcome, outcomeIndex) => (
                                <ListItem key={outcomeIndex} sx={{ py: 0.5 }}>
                                  <ListItemIcon sx={{ minWidth: 32 }}>
                                    <CheckCircleIcon color="success" fontSize="small" />
                                  </ListItemIcon>
                                  <ListItemText primary={outcome} />
                                </ListItem>
                              ))}
                            </List>
                          </Box>
                        </AccordionDetails>
                      </Accordion>
                    ))}
                  </CardContent>
                </Card>

                {/* 스킬 추천 */}
                <Card sx={{ mb: 3 }}>
                  <CardContent>
                    <Typography variant="h5" sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
                      <SchoolIcon sx={{ mr: 1, color: 'info.main' }} />
                      추천 스킬
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {result.skill_recommendations.map((skill, index) => (
                        <Chip
                          key={index}
                          label={skill}
                          color="info"
                          variant="outlined"
                          size="medium"
                        />
                      ))}
                    </Box>
                  </CardContent>
                </Card>

                {/* 커리어 패스 */}
                <Card>
                  <CardContent>
                    <Typography variant="h5" sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
                      <WorkIcon sx={{ mr: 1, color: 'success.main' }} />
                      커리어 패스 제안
                    </Typography>
                    <List>
                      {result.career_path_suggestions.map((suggestion, index) => (
                        <ListItem key={index} sx={{ py: 1 }}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <StarIcon color="success" />
                          </ListItemIcon>
                          <ListItemText 
                            primary={suggestion}
                            primaryTypographyProps={{ variant: 'body1', fontWeight: 500 }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </CardContent>
                </Card>
              </Box>
            ) : (
              <Paper elevation={0} sx={{ p: 4, textAlign: 'center', color: 'text.secondary' }}>
                <FeedbackIcon sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
                <Typography variant="h6" sx={{ mb: 1 }}>
                  CV 피드백 결과
                </Typography>
                <Typography variant="body2">
                  왼쪽에서 CV 분석 ID를 입력하고 피드백을 받아보세요.
                </Typography>
              </Paper>
            )}
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default CVFeedbackPage; 