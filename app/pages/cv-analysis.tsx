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
  ListItemIcon,
  Select,
  MenuItem,
  FormControl,
  InputLabel
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
import CVUploader from '../components/CVUploader';
import RadarChart from '../components/RadarChart';
import { analyzeCVFromFile } from '../api/api';

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
  const [field, setField] = useState('Machine Learning / Deep Learning (ML/DL)');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CVAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
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

  const handleFileChange = (file: File | null) => {
    setSelectedFile(file);
    setError(null);
  };

  const handleFieldChange = (event: any) => {
    setField(event.target.value);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError('CV 파일을 업로드해주세요.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await analyzeCVFromFile(selectedFile, field);
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

        <Box sx={{ display: 'flex', gap: 4, flexDirection: { xs: 'column', md: 'row' } }}>
          {/* 입력 섹션 */}
          <Box sx={{ flex: 1 }}>
            <Paper elevation={0} sx={{ p: 4, height: 'fit-content' }}>
              <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
                CV 파일 업로드
              </Typography>

              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel id="field-select-label">분야 선택</InputLabel>
                <Select
                  labelId="field-select-label"
                  id="field-select"
                  value={field}
                  label="분야 선택"
                  onChange={handleFieldChange}
                >
                  {fields.map((option) => (
                    <MenuItem key={option} value={option}>
                      {option}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* 파일 업로드 */}
              <CVUploader onFileChange={handleFileChange} />

              <Button
                variant="contained"
                fullWidth
                size="large"
                onClick={handleAnalyze}
                disabled={loading || !selectedFile}
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
          </Box>

          {/* 결과 섹션 */}
          <Box sx={{ flex: 1 }}>
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
                      <RadarChart data={result.radar_chart_data} />
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
                  왼쪽에서 CV 파일을 업로드하고 분석을 시작하세요.
                </Typography>
              </Paper>
            )}
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default CVAnalysisPage; 