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
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Star as StarIcon,
  Home
} from '@mui/icons-material';
import { useRouter } from 'next/router';

interface CVAnalysisResult {
  id: string;
  cv_text: string;
  skills: string[];
  experiences: any[];
  strengths: string[];
  weaknesses: string[];
  radar_chart_data: any;
  created_at: string;
}

const CVAnalysisPage: React.FC = () => {
  const [cvText, setCvText] = useState('');
  const [field, setField] = useState('Machine Learning / Deep Learning (ML/DL)');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CVAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const fields = [
    'Natural Language Processing (NLP)',
    'Computer Vision (CV)',
    'Multimodal',
    'Machine Learning / Deep Learning (ML/DL)'
  ];

  const handleGoHome = () => {
    router.push('/');
  };

  const handleAnalyze = async () => {
    if (!cvText.trim()) {
      setError('CV 내용을 입력해주세요.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/cv/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          cv_text: cvText,
          field: field
        }),
      });

      if (!response.ok) {
        throw new Error('CV 분석 중 오류가 발생했습니다.');
      }

      const data = await response.json();
      setResult(data);
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
            CV 분석
          </Typography>
          <Typography variant="h6" color="text.secondary">
            AI가 당신의 CV를 분석하여 강점과 개선점을 제시합니다
          </Typography>
        </Box>

        <Grid container spacing={4}>
          {/* 입력 섹션 */}
          <Grid item xs={12} md={6}>
            <Paper elevation={0} sx={{ p: 4, height: 'fit-content' }}>
              <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
                CV 내용 입력
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

              <TextField
                multiline
                rows={12}
                fullWidth
                label="CV 내용을 입력하세요"
                value={cvText}
                onChange={(e) => setCvText(e.target.value)}
                placeholder="예시: Python, TensorFlow, PyTorch 경험. 머신러닝 프로젝트 3개 완료. 논문 2편 발표..."
                sx={{ mb: 3 }}
              />

              <Button
                variant="contained"
                fullWidth
                size="large"
                onClick={handleAnalyze}
                disabled={loading || !cvText.trim()}
                startIcon={loading ? <CircularProgress size={20} /> : <AssessmentIcon />}
                sx={{ py: 1.5 }}
              >
                {loading ? '분석 중...' : 'CV 분석 시작'}
              </Button>

              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}
            </Paper>
          </Grid>

          {/* 결과 섹션 */}
          <Grid item xs={12} md={6}>
            {result ? (
              <Paper elevation={0} sx={{ p: 4 }}>
                <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
                  분석 결과
                </Typography>

                {/* 스킬 섹션 */}
                <Card sx={{ mb: 3 }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                      <StarIcon sx={{ mr: 1, color: 'primary.main' }} />
                      보유 스킬
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {result.skills.map((skill, index) => (
                        <Chip
                          key={index}
                          label={skill}
                          color="primary"
                          variant="outlined"
                          size="small"
                        />
                      ))}
                    </Box>
                  </CardContent>
                </Card>

                {/* 강점 섹션 */}
                <Card sx={{ mb: 3 }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                      <CheckCircleIcon sx={{ mr: 1, color: 'success.main' }} />
                      강점
                    </Typography>
                    <List dense>
                      {result.strengths.map((strength, index) => (
                        <ListItem key={index} sx={{ py: 0.5 }}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <CheckCircleIcon color="success" fontSize="small" />
                          </ListItemIcon>
                          <ListItemText primary={strength} />
                        </ListItem>
                      ))}
                    </List>
                  </CardContent>
                </Card>

                {/* 약점 섹션 */}
                <Card sx={{ mb: 3 }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                      <CancelIcon sx={{ mr: 1, color: 'error.main' }} />
                      개선점
                    </Typography>
                    <List dense>
                      {result.weaknesses.map((weakness, index) => (
                        <ListItem key={index} sx={{ py: 0.5 }}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <CancelIcon color="error" fontSize="small" />
                          </ListItemIcon>
                          <ListItemText primary={weakness} />
                        </ListItem>
                      ))}
                    </List>
                  </CardContent>
                </Card>

                {/* 레이더 차트 데이터 */}
                {result.radar_chart_data && (
                  <Card>
                    <CardContent>
                      <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                        <TrendingUpIcon sx={{ mr: 1, color: 'info.main' }} />
                        능력 평가
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {Object.entries(result.radar_chart_data.scores || {}).map(([category, score]) => (
                          <Chip
                            key={category}
                            label={`${category}: ${Math.round(Number(score) * 100)}%`}
                            color={Number(score) > 0.7 ? 'success' : Number(score) > 0.4 ? 'warning' : 'error'}
                            variant="outlined"
                            size="small"
                          />
                        ))}
                      </Box>
                    </CardContent>
                  </Card>
                )}
              </Paper>
            ) : (
              <Paper elevation={0} sx={{ p: 4, textAlign: 'center', color: 'text.secondary' }}>
                <PsychologyIcon sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
                <Typography variant="h6" sx={{ mb: 1 }}>
                  CV 분석 결과
                </Typography>
                <Typography variant="body2">
                  왼쪽에서 CV 내용을 입력하고 분석을 시작하세요.
                </Typography>
              </Paper>
            )}
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default CVAnalysisPage; 