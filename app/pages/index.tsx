import React from "react";
import { 
  Box, 
  Typography, 
  Button, 
  Container, 
  Grid, 
  Card, 
  CardContent, 
  Paper,
  Chip,
  Stack,
  useTheme,
  useMediaQuery
} from "@mui/material";
import { useRouter } from "next/router";
import FlightTakeoffIcon from "@mui/icons-material/FlightTakeoff";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import SchoolIcon from "@mui/icons-material/School";
import FeedbackIcon from "@mui/icons-material/Feedback";
import TipsAndUpdatesIcon from "@mui/icons-material/TipsAndUpdates";
import AssignmentIcon from "@mui/icons-material/Assignment";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import PsychologyIcon from "@mui/icons-material/Psychology";
import VisibilityIcon from "@mui/icons-material/Visibility";
import SpeedIcon from "@mui/icons-material/Speed";

const features = [
  {
    icon: <TrendingUpIcon sx={{ fontSize: 40, color: '#3B82F6' }} />,
    title: "논문 트렌드 분석",
    description: "최신 AI/ML 연구 동향을 실시간으로 분석하여 관심 분야의 핫한 주제를 파악하세요.",
    color: "linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%)",
    borderColor: "#3B82F6",
    path: "/trends"
  },
  {
    icon: <SchoolIcon sx={{ fontSize: 40, color: '#0EA5E9' }} />,
    title: "논문 비교 분석",
    description: "당신의 연구 아이디어와 기존 논문들을 비교하여 차별화 전략을 제시합니다.",
    color: "linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%)",
    borderColor: "#0EA5E9",
    path: "/comparison"
  },
  {
    icon: <PsychologyIcon sx={{ fontSize: 40, color: '#F59E0B' }} />,
    title: "CV 분석",
    description: "AI가 당신의 CV를 분석하여 강점과 개선점을 객관적으로 평가합니다.",
    color: "linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%)",
    borderColor: "#F59E0B",
    path: "/cv-analysis"
  },
  {
    icon: <FeedbackIcon sx={{ fontSize: 40, color: '#10B981' }} />,
    title: "CV 피드백",
    description: "AI가 제안하는 개선 프로젝트와 커리어 방향을 확인하세요.",
    color: "linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%)",
    borderColor: "#10B981",
    path: "/cv-feedback"
  },
  {
    icon: <AssignmentIcon sx={{ fontSize: 40, color: '#8B5CF6' }} />,
    title: "CV QA",
    description: "CV 기반 면접 질의응답으로 면접 준비를 도와드립니다.",
    color: "linear-gradient(135deg, #F3E8FF 0%, #E9D5FF 100%)",
    borderColor: "#8B5CF6",
    path: "/cv-qa"
  },
  {
    icon: <AutoAwesomeIcon sx={{ fontSize: 40, color: '#EC4899' }} />,
    title: "데일리 팟캐스트",
    description: "AI가 분석한 최신 논문들을 음성으로 들을 수 있습니다.",
    color: "linear-gradient(135deg, #FCE7F3 0%, #FBCFE8 100%)",
    borderColor: "#EC4899",
    path: "/podcast"
  }
];

const stats = [
  { number: "19,817", label: "분석된 논문" },
  { number: "500+", label: "추천된 교수진" },
  { number: "95%", label: "만족도" },
  { number: "24/7", label: "실시간 분석" }
];

export default function HomePage() {
  const router = useRouter();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleGetStarted = () => {
    router.push('/dashboard');
  };

  return (
    <Box sx={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%)',
      overflow: 'hidden'
    }}>
      {/* Navigation Header */}
      <Box sx={{ 
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 1000,
        background: 'rgba(31, 41, 55, 0.95)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        <Container maxWidth="lg">
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            py: 2
          }}>
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center'
            }}>
              <FlightTakeoffIcon sx={{ 
                fontSize: 32, 
                color: '#3B82F6',
                mr: 1
              }} />
              <Typography variant="h5" sx={{ 
                fontWeight: 700,
                background: 'linear-gradient(135deg, #3B82F6 0%, #10B981 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
                CVPilot
              </Typography>
            </Box>
            
            <Button
              variant="contained"
              onClick={handleGetStarted}
              sx={{
                background: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%)'
                }
              }}
            >
              분석 시작하기
            </Button>
          </Box>
        </Container>
      </Box>
      
      {/* Hero Section */}
      <Box sx={{ 
        position: 'relative',
        background: 'linear-gradient(135deg, #1F2937 0%, #374151 100%)',
        color: 'white',
        pt: { xs: 12, md: 16 },
        pb: { xs: 8, md: 12 },
        overflow: 'hidden'
      }}>
        {/* Background Pattern */}
        <Box sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 20% 80%, rgba(59, 130, 246, 0.1) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(16, 185, 129, 0.1) 0%, transparent 50%)',
          zIndex: 1
        }} />
        
        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 2 }}>
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
            gap: 4,
            alignItems: 'center'
          }}>
            <Box sx={{ textAlign: { xs: 'center', md: 'left' } }}>
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: { xs: 'center', md: 'flex-start' },
                mb: 3
              }}>
                <FlightTakeoffIcon sx={{ 
                  fontSize: 48, 
                  color: '#3B82F6',
                  mr: 2,
                  filter: 'drop-shadow(0 4px 8px rgba(59, 130, 246, 0.3))'
                }} />
                <Typography variant="h3" sx={{ 
                  fontWeight: 700,
                  background: 'linear-gradient(135deg, #3B82F6 0%, #10B981 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent'
                }}>
                  CVPilot
                </Typography>
              </Box>
              
              <Typography variant="h2" sx={{ 
                fontWeight: 800, 
                mb: 3,
                fontSize: { xs: '2.5rem', md: '3.5rem' },
                lineHeight: 1.2,
                color: '#FFFFFF',
                textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)',
                letterSpacing: '-0.02em'
              }}>
                AI로 만드는<br />
                완벽한 학술 커리어
              </Typography>
              
              <Typography variant="h6" sx={{ 
                mb: 4, 
                color: '#F3F4F6',
                lineHeight: 1.7,
                maxWidth: 500,
                fontSize: '1.125rem',
                fontWeight: 500,
                textShadow: '0 1px 2px rgba(0, 0, 0, 0.2)'
              }}>
                최신 AI 기술로 당신의 CV를 분석하고, 관심 분야의 트렌드를 파악하여 
                완벽한 학술 커리어 로드맵을 제시합니다.
              </Typography>
              
                                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                    <Button
                      variant="contained"
                      size="large"
                      onClick={handleGetStarted}
                      sx={{
                        py: 2,
                        px: 4,
                        fontSize: '1.1rem',
                        background: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%)',
                          transform: 'translateY(-2px)',
                          boxShadow: '0 8px 25px rgba(59, 130, 246, 0.3)'
                        }
                      }}
                    >
                      CV 분석
                    </Button>
                    <Button
                      variant="outlined"
                      size="large"
                      onClick={() => router.push('/trends')}
                      sx={{
                        py: 2,
                        px: 4,
                        fontSize: '1.1rem',
                        borderColor: 'rgba(255, 255, 255, 0.3)',
                        color: 'white',
                        '&:hover': {
                          borderColor: 'white',
                          backgroundColor: 'rgba(255, 255, 255, 0.1)'
                        }
                      }}
                    >
                      트렌드 분석
                    </Button>
                    <Button
                      variant="outlined"
                      size="large"
                      onClick={() => router.push('/papers')}
                      sx={{
                        py: 2,
                        px: 4,
                        fontSize: '1.1rem',
                        borderColor: 'rgba(255, 255, 255, 0.3)',
                        color: 'white',
                        '&:hover': {
                          borderColor: 'white',
                          backgroundColor: 'rgba(255, 255, 255, 0.1)'
                        }
                      }}
                    >
                      논문 분석
                    </Button>
                    <Button
                      variant="outlined"
                      size="large"
                      onClick={() => router.push('/comparison')}
                      sx={{
                        py: 2,
                        px: 4,
                        fontSize: '1.1rem',
                        borderColor: 'rgba(255, 255, 255, 0.3)',
                        color: 'white',
                        '&:hover': {
                          borderColor: 'white',
                          backgroundColor: 'rgba(255, 255, 255, 0.1)'
                        }
                      }}
                    >
                      방법론 비교
                    </Button>
                  </Stack>
            </Box>
            
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'center',
              position: 'relative'
            }}>
              <Paper sx={{
                p: 4,
                background: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: 4,
                maxWidth: 400,
                width: '100%'
              }}>
                <Box sx={{ textAlign: 'center', mb: 3 }}>
                  <PsychologyIcon sx={{ fontSize: 60, color: '#3B82F6', mb: 2 }} />
                  <Typography variant="h5" sx={{ 
                    fontWeight: 700, 
                    mb: 1,
                    color: '#FFFFFF',
                    textShadow: '0 1px 2px rgba(0, 0, 0, 0.3)'
                  }}>
                    AI 분석 결과
                  </Typography>
                  <Typography variant="body2" sx={{ 
                    color: '#E5E7EB',
                    fontWeight: 500,
                    textShadow: '0 1px 2px rgba(0, 0, 0, 0.2)'
                  }}>
                    실시간으로 업데이트되는 분석 결과
                  </Typography>
                </Box>
                
                <Stack spacing={2}>
                  {[
                    { label: "논문 트렌드", progress: 85 },
                    { label: "교수 추천", progress: 92 },
                    { label: "CV 분석", progress: 78 },
                    { label: "개선 방향", progress: 88 }
                  ].map((item, index) => (
                    <Box key={index}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2" sx={{ 
                          color: '#F3F4F6',
                          fontWeight: 600,
                          textShadow: '0 1px 2px rgba(0, 0, 0, 0.2)'
                        }}>
                          {item.label}
                        </Typography>
                        <Typography variant="body2" sx={{ 
                          color: '#3B82F6',
                          fontWeight: 700,
                          textShadow: '0 1px 2px rgba(0, 0, 0, 0.2)'
                        }}>
                          {item.progress}%
                        </Typography>
                      </Box>
                      <Box sx={{
                        width: '100%',
                        height: 6,
                        backgroundColor: 'rgba(255, 255, 255, 0.2)',
                        borderRadius: 3,
                        overflow: 'hidden'
                      }}>
                        <Box sx={{
                          width: `${item.progress}%`,
                          height: '100%',
                          background: 'linear-gradient(90deg, #3B82F6 0%, #10B981 100%)',
                          borderRadius: 3,
                          transition: 'width 0.5s ease'
                        }} />
                      </Box>
                    </Box>
                  ))}
                </Stack>
              </Paper>
            </Box>
          </Box>
        </Container>
      </Box>

      {/* Stats Section */}
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' },
          gap: 4
        }}>
          {stats.map((stat, index) => (
            <Box key={index} sx={{ textAlign: 'center' }}>
              <Typography variant="h3" sx={{ 
                fontWeight: 800, 
                color: '#3B82F6',
                mb: 1,
                textShadow: '0 2px 4px rgba(59, 130, 246, 0.2)'
              }}>
                {stat.number}
              </Typography>
              <Typography variant="body1" sx={{ 
                color: '#374151',
                fontWeight: 600,
                fontSize: '1.1rem'
              }}>
                {stat.label}
              </Typography>
            </Box>
          ))}
        </Box>
      </Container>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Box sx={{ textAlign: 'center', mb: 8 }}>
          <Typography variant="h3" sx={{ 
            fontWeight: 800, 
            mb: 3,
            color: '#1F2937',
            textShadow: '0 2px 4px rgba(31, 41, 55, 0.1)'
          }}>
            강력한 기능들
          </Typography>
          <Typography variant="h6" sx={{ 
            color: '#4B5563', 
            maxWidth: 600, 
            mx: 'auto',
            fontWeight: 600,
            fontSize: '1.25rem'
          }}>
            AI 기술을 활용한 종합적인 학술 커리어 분석 서비스
          </Typography>
        </Box>
        
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' },
          gap: 4
        }}>
          {features.map((feature, index) => (
            <Card 
              key={index} 
              sx={{
                height: '100%',
                background: feature.color,
                border: `2px solid ${feature.borderColor}`,
                borderRadius: 3,
                transition: 'all 0.3s ease',
                cursor: 'pointer',
                '&:hover': {
                  transform: 'translateY(-8px)',
                  boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)'
                }
              }}
              onClick={() => router.push(feature.path)}
            >
              <CardContent sx={{ p: 4, textAlign: 'center' }}>
                <Box sx={{ mb: 3 }}>
                  {feature.icon}
                </Box>
                <Typography variant="h5" sx={{ 
                  fontWeight: 700, 
                  mb: 2,
                  color: '#1F2937'
                }}>
                  {feature.title}
                </Typography>
                <Typography variant="body1" sx={{ 
                  color: '#4B5563', 
                  lineHeight: 1.7,
                  fontWeight: 500
                }}>
                  {feature.description}
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Box>
      </Container>

      {/* CTA Section */}
      <Box sx={{ 
        background: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)',
        color: 'white',
        py: 8
      }}>
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h3" sx={{ 
              fontWeight: 800, 
              mb: 3,
              textShadow: '0 2px 4px rgba(0, 0, 0, 0.2)'
            }}>
              지금 바로 시작하세요
            </Typography>
            <Typography variant="h6" sx={{ 
              mb: 4, 
              color: '#E5E7EB',
              fontWeight: 600,
              fontSize: '1.25rem',
              textShadow: '0 1px 2px rgba(0, 0, 0, 0.2)'
            }}>
              AI가 제시하는 완벽한 학술 커리어 로드맵을 경험해보세요
            </Typography>
            <Button
              variant="contained"
              size="large"
              onClick={handleGetStarted}
              sx={{
                py: 2,
                px: 6,
                fontSize: '1.2rem',
                background: 'white',
                color: '#3B82F6',
                '&:hover': {
                  background: '#F8FAFC',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 8px 25px rgba(0, 0, 0, 0.2)'
                }
              }}
            >
              무료로 분석 시작하기
            </Button>
          </Box>
        </Container>
      </Box>
    </Box>
  );
}
