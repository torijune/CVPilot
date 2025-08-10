import React, { useEffect, useRef, useState } from "react";
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

import TipsAndUpdatesIcon from "@mui/icons-material/TipsAndUpdates";
import AssignmentIcon from "@mui/icons-material/Assignment";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import PsychologyIcon from "@mui/icons-material/Psychology";
import VisibilityIcon from "@mui/icons-material/Visibility";
import SpeedIcon from "@mui/icons-material/Speed";
import BusinessIcon from "@mui/icons-material/Business";

// 스크롤 애니메이션을 위한 커스텀 훅 (반복 가능)
const useScrollAnimation = () => {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        // 요소가 화면에 들어오면 보이게, 나가면 숨기게
        setIsVisible(entry.isIntersecting);
      },
      {
        threshold: 0.05,  // 5%만 보여도 렌더링 시작
        rootMargin: '0px 0px -100px 0px'  // 하단에서 100px 전까지 렌더링 유지
      }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current);
      }
    };
  }, []);

  return [ref, isVisible] as const;
};

const featuresTop = [
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
  }
];

const featuresBottom = [
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
  },
  {
    icon: <BusinessIcon sx={{ fontSize: 40, color: '#6366F1' }} />,
    title: "연구실 분석",
    description: "AI가 연구실의 최신 연구 동향을 분석하여 인사이트를 제공합니다.",
    color: "linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%)",
    borderColor: "#6366F1",
    path: "/lab_analysis"
  }
];

const stats = [
  { number: "6+", label: "AI 분석 모듈", icon: "🤖" },
  { number: "∞", label: "무제한 분석", icon: "♾️" },
  { number: "실시간", label: "분석 속도", icon: "⚡" },
  { number: "무료", label: "서비스 이용", icon: "🎁" }
];

export default function HomePage() {
  const router = useRouter();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // 각 섹션의 애니메이션 상태
  const [statsRef, statsVisible] = useScrollAnimation();
  const [featuresTopRef, featuresTopVisible] = useScrollAnimation();
  const [featuresBottomRef, featuresBottomVisible] = useScrollAnimation();
  const [howItWorksRef, howItWorksVisible] = useScrollAnimation();
  const [techRef, techVisible] = useScrollAnimation();
  const [testimonialsRef, testimonialsVisible] = useScrollAnimation();

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
        pt: { xs: 8, md: 12 },
        pb: { xs: 6, md: 8 },
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
              
                            <Box sx={{ 
                display: 'grid',
                gridTemplateColumns: { xs: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' },
                gap: 2,
                mt: 2
              }}>
                {[
                  { 
                    icon: '🎯', 
                    title: '스마트 분석', 
                    subtitle: '맞춤형 AI 컨설팅',
                    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                  },
                  { 
                    icon: '⚡', 
                    title: '실시간 인사이트', 
                    subtitle: '즉시 결과 확인',
                    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
                  },
                  { 
                    icon: '🚀', 
                    title: '커리어 부스터', 
                    subtitle: '경쟁력 강화 솔루션',
                    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
                  }
                ].map((item, index) => (
                  <Paper
                    key={index}
                    sx={{
                      p: 3,
                      background: 'rgba(255, 255, 255, 0.15)',
                      backdropFilter: 'blur(20px)',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      borderRadius: 3,
                      textAlign: 'center',
                      transition: 'all 0.3s ease',
                      position: 'relative',
                      overflow: 'hidden',
                      '&:hover': {
                        transform: 'translateY(-8px)',
                        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
                        background: 'rgba(255, 255, 255, 0.25)',
                      },
                      '&::before': {
                        content: '""',
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        height: '3px',
                        background: item.gradient,
                        borderRadius: '3px 3px 0 0'
                      }
                    }}
                  >
                    <Typography sx={{ fontSize: '2rem', mb: 1 }}>
                      {item.icon}
                    </Typography>
                    <Typography variant="h6" sx={{ 
                      fontWeight: 700, 
                      color: 'white', 
                      mb: 0.5,
                      textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)'
                    }}>
                      {item.title}
                    </Typography>
                    <Typography variant="caption" sx={{ 
                      color: 'rgba(255, 255, 255, 0.8)',
                      fontSize: '0.8rem',
                      textShadow: '0 1px 2px rgba(0, 0, 0, 0.3)'
                    }}>
                      {item.subtitle}
                    </Typography>
                  </Paper>
                ))}
              </Box>
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
              <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box 
          ref={statsRef}
          sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' },
            gap: 4,
            opacity: statsVisible ? 1 : 0,
            transform: statsVisible ? 'translateY(0)' : 'translateY(50px)',
            transition: 'all 0.8s ease-out',
          }}
        >
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

      {/* Features Section - Top Row */}
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box 
          ref={featuresTopRef}
          sx={{ 
            textAlign: 'center', 
            mb: 4,
            opacity: featuresTopVisible ? 1 : 0,
            transform: featuresTopVisible ? 'translateY(0)' : 'translateY(50px)',
            transition: 'all 0.8s ease-out',
          }}
        >
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
          {featuresTop.map((feature, index) => (
            <Card 
              key={index} 
              sx={{
                height: '100%',
                background: feature.color,
                border: `2px solid ${feature.borderColor}`,
                borderRadius: 3,
                transition: 'all 0.6s ease',
                cursor: 'pointer',
                opacity: featuresTopVisible ? 1 : 0,
                transform: featuresTopVisible ? 'translateY(0)' : 'translateY(30px)',
                transitionDelay: featuresTopVisible ? `${index * 0.1}s` : '0s',
                '&:hover': {
                  transform: featuresTopVisible ? 'translateY(-8px)' : 'translateY(30px)',
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

      {/* Features Section - Bottom Row */}
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box 
          ref={featuresBottomRef}
          sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' },
            gap: 4
          }}
        >
          {featuresBottom.map((feature, index) => (
            <Card 
              key={index} 
              sx={{
                height: '100%',
                background: feature.color,
                border: `2px solid ${feature.borderColor}`,
                borderRadius: 3,
                transition: 'all 0.6s ease',
                cursor: 'pointer',
                opacity: featuresBottomVisible ? 1 : 0,
                transform: featuresBottomVisible ? 'translateY(0)' : 'translateY(30px)',
                transitionDelay: featuresBottomVisible ? `${index * 0.1}s` : '0s',
                '&:hover': {
                  transform: featuresBottomVisible ? 'translateY(-8px)' : 'translateY(30px)',
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

      {/* How It Works Section */}
      <Box 
        ref={howItWorksRef}
        sx={{ 
          py: 6,
          background: 'linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%)',
          position: 'relative',
          opacity: howItWorksVisible ? 1 : 0,
          transform: howItWorksVisible ? 'translateY(0)' : 'translateY(50px)',
          transition: 'all 1.2s ease-out',
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography variant="h3" sx={{ 
              fontWeight: 800, 
              mb: 3,
              color: '#1F2937'
            }}>
              🚀 3단계로 완성하는 AI 분석
            </Typography>
            <Typography variant="h6" sx={{ 
              color: '#4B5563', 
              maxWidth: 600, 
              mx: 'auto',
              fontWeight: 500
            }}>
              간단한 3단계로 당신의 학술 커리어를 분석하고 개선 방향을 제시받으세요
            </Typography>
          </Box>
          
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' },
            gap: 6,
            position: 'relative'
          }}>
            {[
              {
                step: '01',
                title: '업로드 & 입력',
                description: 'CV 파일을 업로드하거나 관심 분야를 선택하세요',
                icon: '📄',
                gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
              },
              {
                step: '02',
                title: 'AI 분석',
                description: '최신 AI 기술로 데이터를 분석하고 인사이트를 추출합니다',
                icon: '🤖',
                gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
              },
              {
                step: '03',
                title: '결과 확인',
                description: '개선 방향과 맞춤형 추천을 받아 커리어를 발전시키세요',
                icon: '📊',
                gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
              }
            ].map((item, index) => (
              <Box key={index} sx={{ position: 'relative', textAlign: 'center' }}>
                {/* Connecting Line */}
                {index < 2 && (
                  <Box sx={{
                    position: 'absolute',
                    top: '60px',
                    right: { xs: 'auto', md: '-3rem' },
                    bottom: { xs: '-3rem', md: 'auto' },
                    left: { xs: '50%', md: 'auto' },
                    width: { xs: '2px', md: '6rem' },
                    height: { xs: '3rem', md: '2px' },
                    background: 'linear-gradient(135deg, #E2E8F0 0%, #CBD5E1 100%)',
                    transform: { xs: 'translateX(-50%)', md: 'none' },
                    zIndex: 1,
                    display: { xs: 'block', md: 'block' }
                  }} />
                )}
                
                <Paper sx={{
                  p: 4,
                  background: 'rgba(255, 255, 255, 0.9)',
                  backdropFilter: 'blur(20px)',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  borderRadius: 4,
                  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
                  transition: 'all 0.3s ease',
                  position: 'relative',
                  zIndex: 2,
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15)',
                  }
                }}>
                  <Box sx={{
                    width: 80,
                    height: 80,
                    borderRadius: '50%',
                    background: item.gradient,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mx: 'auto',
                    mb: 3,
                    fontSize: '2rem',
                    boxShadow: '0 8px 24px rgba(0, 0, 0, 0.15)'
                  }}>
                    {item.icon}
                  </Box>
                  
                  <Typography variant="h2" sx={{
                    position: 'absolute',
                    top: 20,
                    right: 20,
                    fontSize: '4rem',
                    fontWeight: 900,
                    color: 'rgba(0, 0, 0, 0.05)',
                    lineHeight: 1,
                    zIndex: 0
                  }}>
                    {item.step}
                  </Typography>
                  
                  <Typography variant="h5" sx={{ 
                    fontWeight: 700, 
                    mb: 2,
                    color: '#1F2937'
                  }}>
                    {item.title}
                  </Typography>
                  <Typography sx={{ 
                    color: '#4B5563', 
                    lineHeight: 1.7,
                    fontWeight: 500
                  }}>
                    {item.description}
                  </Typography>
                </Paper>
              </Box>
            ))}
          </Box>
        </Container>
      </Box>

      {/* Technologies Section */}
      <Box 
        ref={techRef}
        sx={{ 
          py: 6, 
          background: '#1F2937',
          opacity: techVisible ? 1 : 0,
          transform: techVisible ? 'translateY(0)' : 'translateY(50px)',
          transition: 'all 0.8s ease-out',
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography variant="h3" sx={{ 
              fontWeight: 800, 
              mb: 3,
              color: 'white'
            }}>
              🔬 최신 AI 기술 스택
            </Typography>
            <Typography variant="h6" sx={{ 
              color: '#9CA3AF', 
              maxWidth: 600, 
              mx: 'auto',
              fontWeight: 500
            }}>
              업계 최고 수준의 AI 모델과 기술을 활용하여 정확한 분석을 제공합니다
            </Typography>
          </Box>
          
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' },
            gap: 4
          }}>
            {[
              { name: 'GPT-4', description: '자연어 처리', icon: '🧠' },
              { name: 'Embedding API', description: '벡터 임베딩', icon: '🔗' },
              { name: 'Next.js', description: '프론트엔드', icon: '⚛️' },
              { name: 'FastAPI', description: '백엔드 API', icon: '🚀' },
              { name: 'PostgreSQL', description: '데이터베이스', icon: '🗄️' },
              { name: 'Docker', description: '컨테이너화', icon: '🐳' },
              { name: 'TypeScript', description: '타입 안정성', icon: '📘' },
              { name: 'Material-UI', description: 'UI 컴포넌트', icon: '🎨' }
            ].map((tech, index) => (
              <Paper key={index} sx={{
                p: 3,
                textAlign: 'center',
                background: 'rgba(255, 255, 255, 0.05)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: 3,
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  background: 'rgba(255, 255, 255, 0.1)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                }
              }}>
                <Typography sx={{ fontSize: '2.5rem', mb: 1 }}>
                  {tech.icon}
                </Typography>
                <Typography variant="h6" sx={{ 
                  fontWeight: 700, 
                  color: 'white',
                  mb: 1
                }}>
                  {tech.name}
                </Typography>
                <Typography variant="caption" sx={{ 
                  color: '#9CA3AF',
                  fontSize: '0.9rem'
                }}>
                  {tech.description}
                </Typography>
              </Paper>
            ))}
          </Box>
        </Container>
      </Box>

      {/* Testimonials Section */}
      <Box 
        ref={testimonialsRef}
        sx={{ 
          py: 6, 
          background: 'linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%)',
          opacity: testimonialsVisible ? 1 : 0,
          transform: testimonialsVisible ? 'translateY(0)' : 'translateY(50px)',
          transition: 'all 0.8s ease-out',
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography variant="h3" sx={{ 
              fontWeight: 800, 
              mb: 3,
              color: '#1F2937'
            }}>
              💬 사용자 후기
            </Typography>
            <Typography variant="h6" sx={{ 
              color: '#4B5563', 
              maxWidth: 600, 
              mx: 'auto',
              fontWeight: 500
            }}>
              CVPilot을 통해 성공적인 학술 커리어를 쌓고 있는 사용자들의 이야기
            </Typography>
          </Box>
          
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' },
            gap: 4
          }}>
            {[
              {
                name: '김연구',
                role: 'KAIST 석사과정',
                content: 'CV 분석을 통해 부족한 부분을 명확히 파악할 수 있었고, 연구실 분석으로 최적의 랩을 찾았습니다.',
                rating: 5,
                avatar: '👨‍🎓'
              },
              {
                name: '이논문',
                role: '서울대 박사과정',
                content: '논문 트렌드 분석 덕분에 최신 연구 동향을 빠르게 파악하고 연구 방향을 설정할 수 있었어요.',
                rating: 5,
                avatar: '👩‍🔬'
              },
              {
                name: '박학위',
                role: '연세대 학부생',
                content: '대학원 진학 준비에 큰 도움이 되었습니다. 특히 연구실 분석 기능이 정말 유용했어요!',
                rating: 5,
                avatar: '👨‍💻'
              }
            ].map((testimonial, index) => (
              <Paper key={index} sx={{
                p: 4,
                background: 'rgba(255, 255, 255, 0.9)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                borderRadius: 4,
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15)',
                }
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Typography sx={{ fontSize: '3rem', mr: 2 }}>
                    {testimonial.avatar}
                  </Typography>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 700, color: '#1F2937' }}>
                      {testimonial.name}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#6B7280' }}>
                      {testimonial.role}
                    </Typography>
                  </Box>
                </Box>
                
                <Typography sx={{ 
                  color: '#374151', 
                  lineHeight: 1.7,
                  fontStyle: 'italic',
                  mb: 3
                }}>
                  "{testimonial.content}"
                </Typography>
                
                <Box sx={{ display: 'flex', gap: 0.5 }}>
                  {Array.from({ length: testimonial.rating }).map((_, i) => (
                    <Typography key={i} sx={{ color: '#F59E0B', fontSize: '1.2rem' }}>
                      ⭐
                    </Typography>
                  ))}
                </Box>
              </Paper>
            ))}
          </Box>
        </Container>
      </Box>

      {/* CTA Section */}
      <Box sx={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        py: 6,
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Background Pattern */}
        <Box sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%)',
          zIndex: 1
        }} />
        
        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 2 }}>
          <Box sx={{ textAlign: 'center' }}>
            <Typography sx={{ 
              fontSize: '4rem', 
              mb: 3,
              filter: 'drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1))'
            }}>
              🎓
            </Typography>
            <Typography variant="h3" sx={{ 
              fontWeight: 800, 
              mb: 3,
              textShadow: '0 2px 4px rgba(0, 0, 0, 0.2)',
              background: 'linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              당신의 학술 여정을 함께합니다
            </Typography>
            <Typography variant="h6" sx={{ 
              mb: 4, 
              color: 'rgba(255, 255, 255, 0.9)',
              fontWeight: 500,
              fontSize: '1.25rem',
              textShadow: '0 1px 2px rgba(0, 0, 0, 0.2)',
              maxWidth: 600,
              mx: 'auto',
              lineHeight: 1.6
            }}>
              CVPilot와 함께 더 나은 미래를 설계하고,<br />
              꿈꾸던 학술 커리어를 현실로 만들어보세요
            </Typography>
            
            
          </Box>
        </Container>
      </Box>

      {/* Footer */}
      <Box sx={{ 
        background: '#1F2937',
        color: 'white',
        py: 6
      }}>
        <Container maxWidth="lg">
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: '1fr', md: 'repeat(4, 1fr)' },
            gap: 4,
            mb: 4
          }}>
            {/* 회사 정보 */}
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
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
              <Typography variant="body2" sx={{ 
                color: '#9CA3AF',
                lineHeight: 1.6,
                mb: 2
              }}>
                AI 기반 학술 커리어 분석 플랫폼으로<br />
                연구자들의 성공적인 미래를 지원합니다.
              </Typography>
              <Typography variant="caption" sx={{ 
                color: '#6B7280'
              }}>
                © 2025 CVPilot. All rights reserved.
              </Typography>
            </Box>

            {/* 서비스 */}
            <Box>
              <Typography variant="h6" sx={{ 
                fontWeight: 700, 
                mb: 3,
                color: 'white'
              }}>
                서비스
              </Typography>
                             <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                 {[
                   { name: 'CV 분석', path: '/cv-analysis' },
                   { name: '논문 트렌드 분석', path: '/trends' },
                   { name: '연구실 분석', path: '/lab_analysis' },
                   { name: '논문 비교 분석', path: '/comparison' },
                   { name: '데일리 팟캐스트', path: '/podcast' },
                   { name: 'CV QA', path: '/cv-qa' }
                 ].map((service) => (
                   <Typography 
                     key={service.name} 
                     variant="body2" 
                     onClick={() => router.push(service.path)}
                     sx={{ 
                       color: '#9CA3AF',
                       cursor: 'pointer',
                       transition: 'color 0.2s ease',
                       '&:hover': {
                         color: '#3B82F6'
                       }
                     }}
                   >
                     {service.name}
                   </Typography>
                 ))}
               </Box>
            </Box>

            {/* 회사 */}
            <Box>
              <Typography variant="h6" sx={{ 
                fontWeight: 700, 
                mb: 3,
                color: 'white'
              }}>
                회사
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                {['소개', '팀', '채용', '블로그', '뉴스', '파트너십'].map((item) => (
                  <Typography key={item} variant="body2" sx={{ 
                    color: '#9CA3AF',
                    cursor: 'pointer',
                    transition: 'color 0.2s ease',
                    '&:hover': {
                      color: '#3B82F6'
                    }
                  }}>
                    {item}
                  </Typography>
                ))}
              </Box>
            </Box>

            {/* 지원 */}
            <Box>
              <Typography variant="h6" sx={{ 
                fontWeight: 700, 
                mb: 3,
                color: 'white'
              }}>
                지원
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                <Typography variant="body2" sx={{ 
                  color: '#9CA3AF',
                  cursor: 'pointer',
                  transition: 'color 0.2s ease',
                  '&:hover': {
                    color: '#3B82F6'
                  }
                }}>
                  고객센터
                </Typography>
                <Typography variant="body2" sx={{ 
                  color: '#9CA3AF',
                  cursor: 'pointer',
                  transition: 'color 0.2s ease',
                  '&:hover': {
                    color: '#3B82F6'
                  }
                }}>
                  이용약관
                </Typography>
                <Typography variant="body2" sx={{ 
                  color: '#9CA3AF',
                  cursor: 'pointer',
                  transition: 'color 0.2s ease',
                  '&:hover': {
                    color: '#3B82F6'
                  }
                }}>
                  개인정보처리방침
                </Typography>
                <Typography variant="body2" sx={{ 
                  color: '#9CA3AF'
                }}>
                  📧 dnjswnswkd03@mju.ac.kr
                </Typography>
                <Typography variant="body2" sx={{ 
                  color: '#9CA3AF'
                }}>
                  📞 010-8277-6003
                </Typography>
              </Box>
            </Box>
          </Box>

          {/* 구분선 */}
          <Box sx={{ 
            borderTop: '1px solid #374151',
            pt: 4,
            display: 'flex',
            flexDirection: { xs: 'column', md: 'row' },
            justifyContent: 'space-between',
            alignItems: { xs: 'center', md: 'center' },
            gap: 2
          }}>
            <Typography variant="body2" sx={{ 
              color: '#6B7280',
              textAlign: { xs: 'center', md: 'left' }
            }}>
              Made with ❤️ by CVPilot Team | Powered by Next.js & FastAPI
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 3 }}>
              <Typography 
                variant="body2" 
                component="a"
                href="https://github.com/torijune"
                target="_blank"
                rel="noopener noreferrer"
                sx={{ 
                  color: '#9CA3AF',
                  cursor: 'pointer',
                  transition: 'color 0.2s ease',
                  textDecoration: 'none',
                  '&:hover': {
                    color: '#3B82F6'
                  }
                }}
              >
                🐙 GitHub
              </Typography>
              <Typography 
                variant="body2" 
                component="a"
                href="https://www.linkedin.com/in/%EC%9B%90%EC%A4%80-%EC%9E%A5-765a6a280/"
                target="_blank"
                rel="noopener noreferrer"
                sx={{ 
                  color: '#9CA3AF',
                  cursor: 'pointer',
                  transition: 'color 0.2s ease',
                  textDecoration: 'none',
                  '&:hover': {
                    color: '#3B82F6'
                  }
                }}
              >
                📘 LinkedIn
              </Typography>
            </Box>
          </Box>
        </Container>
      </Box>
    </Box>
  );
}
