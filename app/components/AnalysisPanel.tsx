import React from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Paper from "@mui/material/Paper";
import Divider from "@mui/material/Divider";
import Avatar from "@mui/material/Avatar";
import Chip from "@mui/material/Chip";
import Link from "@mui/material/Link";
import Grid from "@mui/material/Grid";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import SchoolIcon from "@mui/icons-material/School";
import FeedbackIcon from "@mui/icons-material/Feedback";
import TipsAndUpdatesIcon from "@mui/icons-material/TipsAndUpdates";
import AssignmentIcon from "@mui/icons-material/Assignment";

const sections = [
  {
    key: "trend",
    label: "논문 트렌드",
    icon: <TrendingUpIcon />, 
    color: "linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%)",
    iconColor: "#1D4ED8",
    borderColor: "#3B82F6"
  },
  {
    key: "professors",
    label: "교수/대학원",
    icon: <SchoolIcon />, 
    color: "linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%)",
    iconColor: "#0369A1",
    borderColor: "#0EA5E9"
  },
  {
    key: "feedback",
    label: "CV 피드백",
    icon: <FeedbackIcon />, 
    color: "linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%)",
    iconColor: "#D97706",
    borderColor: "#F59E0B"
  },
  {
    key: "improvement",
    label: "개선 방향",
    icon: <TipsAndUpdatesIcon />, 
    color: "linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%)",
    iconColor: "#059669",
    borderColor: "#10B981"
  },
  {
    key: "project",
    label: "프로젝트 가이드",
    icon: <AssignmentIcon />, 
    color: "linear-gradient(135deg, #F3E8FF 0%, #E9D5FF 100%)",
    iconColor: "#7C3AED",
    borderColor: "#8B5CF6"
  }
];

type Props = {
  result: any; // 분석 결과(JSON)
  error?: string | null; // 에러 메시지
};

export default function AnalysisPanel({ result, error }: Props) {
  // 에러가 있으면 에러 메시지 표시
  if (error) {
    return (
      <Box sx={{ 
        p: 3, 
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <Paper
          sx={{
            p: 4,
            background: 'linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%)',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
            borderRadius: 3,
            border: '2px solid #F87171',
            maxWidth: 600,
            width: '100%',
            textAlign: 'center'
          }}
        >
          <Typography variant="h5" sx={{ fontWeight: 700, mb: 2, color: '#DC2626' }}>
            분석 중 오류가 발생했습니다
          </Typography>
          <Typography sx={{ whiteSpace: 'pre-line', color: '#991B1B', fontSize: '1rem' }}>
            {error}
          </Typography>
        </Paper>
      </Box>
    );
  }

  const renderTrendSection = () => {
    const trendText = result?.trend || "논문 트렌드 결과가 여기에 표시됩니다.";
    const paperTrendText = result?.paperTrend || "논문 트렌드 분석 결과가 여기에 표시됩니다.";
    const analysisDetails = result?.analysis_details || "상세 분석 결과가 여기에 표시됩니다.";
    const papers = result?.papers || [];
    const section = sections[0];
    
    return (
      <Paper
        sx={{
          p: 3,
          minHeight: 400,
          background: section.color,
          boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
          borderRadius: 3,
          border: `2px solid ${section.borderColor}`,
          width: '100%',
          display: 'flex',
          flexDirection: 'column',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 20px 40px -10px rgba(0, 0, 0, 0.15)'
          }
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar 
            sx={{ 
              bgcolor: section.iconColor, 
              mr: 2, 
              width: 48, 
              height: 48,
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
            }}
          >
            {section.icon}
          </Avatar>
          <Typography variant="h5" sx={{ fontWeight: 700, color: '#1F2937' }}>
            {section.label}
          </Typography>
        </Box>
        <Divider sx={{ mb: 2, borderColor: section.borderColor }} />
        
        {/* 논문 트렌드 분석 결과 */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 1.5, color: '#1F2937' }}>
            📊 논문 트렌드 분석
          </Typography>
          <Typography sx={{ 
            whiteSpace: 'pre-line', 
            color: '#374151', 
            fontSize: '1rem', 
            lineHeight: 1.7,
            p: 2,
            backgroundColor: 'rgba(255, 255, 255, 0.6)',
            borderRadius: 2,
            border: `1px solid ${section.borderColor}`
          }}>
            {paperTrendText}
          </Typography>
        </Box>
        
        {/* 상세 분석 결과 */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 1.5, color: '#1F2937' }}>
            🔍 상세 분석 결과
          </Typography>
          <Typography sx={{ 
            whiteSpace: 'pre-line', 
            color: '#374151', 
            fontSize: '1rem', 
            lineHeight: 1.7,
            p: 2,
            backgroundColor: 'rgba(255, 255, 255, 0.6)',
            borderRadius: 2,
            border: `1px solid ${section.borderColor}`
          }}>
            {analysisDetails}
          </Typography>
        </Box>
        
        {/* CV 기반 트렌드 분석 */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 1.5, color: '#1F2937' }}>
            📋 CV 기반 트렌드 분석
          </Typography>
        <Typography sx={{ 
          whiteSpace: 'pre-line', 
          color: '#374151', 
          fontSize: '1rem', 
            lineHeight: 1.7,
            p: 2,
            backgroundColor: 'rgba(255, 255, 255, 0.6)',
            borderRadius: 2,
            border: `1px solid ${section.borderColor}`
        }}>
          {trendText}
        </Typography>
        </Box>
        
        {/* 관련 논문 목록 */}
        {papers.length > 0 && (
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, color: '#1F2937' }}>
              📚 참고 논문 ({papers.length}개)
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              {papers.slice(0, 5).map((paper: any, index: number) => (
                <Box key={index} sx={{ 
                  p: 2, 
                  border: `1px solid ${section.borderColor}`, 
                  borderRadius: 2, 
                  backgroundColor: 'rgba(255, 255, 255, 0.8)',
                  backdropFilter: 'blur(10px)',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    transform: 'translateX(4px)',
                    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
                  }
                }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#1F2937', flex: 1 }}>
                      {paper.title}
                    </Typography>
                    <Chip 
                      label={`${paper.conference} ${paper.year}`} 
                      size="small" 
                      sx={{ 
                        backgroundColor: section.iconColor, 
                        color: 'white', 
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        ml: 1
                      }} 
                    />
                  </Box>
                  
                  {/* 관련성 점수 표시 */}
                  {paper.relevance_score && paper.relevance_score > 0 && (
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.75rem' }}>
                        관련성 점수: {(paper.relevance_score * 100).toFixed(1)}%
                      </Typography>
                    </Box>
                  )}
                  
                  {/* URL 링크 */}
                  {paper.url && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Link 
                      href={paper.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      sx={{ 
                        fontSize: '0.875rem', 
                        color: section.iconColor,
                        textDecoration: 'none',
                        fontWeight: 500,
                          display: 'flex',
                          alignItems: 'center',
                          gap: 0.5,
                        '&:hover': { 
                          textDecoration: 'underline',
                          color: section.borderColor
                        }
                      }}
                    >
                        📄 논문 보기 →
                    </Link>
                    </Box>
                  )}
                  
                  {/* URL이 없는 경우 */}
                  {!paper.url && (
                    <Typography variant="caption" sx={{ color: '#9CA3AF', fontSize: '0.75rem' }}>
                      URL 정보 없음
                    </Typography>
                  )}
                </Box>
              ))}
              
              {/* 더 많은 논문이 있는 경우 안내 */}
              {papers.length > 5 && (
                <Box sx={{ 
                  p: 2, 
                  textAlign: 'center',
                  color: '#6B7280',
                  fontSize: '0.875rem'
                }}>
                  ... 외 {papers.length - 5}개의 논문이 더 있습니다
                </Box>
              )}
            </Box>
          </Box>
        )}
      </Paper>
    );
  };

  const renderSection = (section: any) => {
    const content = result?.[section.key] || `${section.label} 결과가 여기에 표시됩니다.`;
    
    return (
      <Paper
        key={section.key}
        sx={{
          p: 3,
          minHeight: 200,
          background: section.color,
          boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
          borderRadius: 3,
          border: `2px solid ${section.borderColor}`,
          width: '100%',
          display: 'flex',
          flexDirection: 'column',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 20px 40px -10px rgba(0, 0, 0, 0.15)'
          }
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar 
            sx={{ 
              bgcolor: section.iconColor, 
              mr: 2, 
              width: 48, 
              height: 48,
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
            }}
          >
            {section.icon}
          </Avatar>
          <Typography variant="h5" sx={{ fontWeight: 700, color: '#1F2937' }}>
            {section.label}
          </Typography>
        </Box>
        <Divider sx={{ mb: 2, borderColor: section.borderColor }} />
        <Typography sx={{ 
          whiteSpace: 'pre-line', 
          color: '#374151', 
          fontSize: '1rem',
          lineHeight: 1.7
        }}>
          {content}
        </Typography>
      </Paper>
    );
  };

  return (
    <Box sx={{ 
      p: 4, 
      height: '100%',
      overflow: 'auto',
      background: 'linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%)'
    }}>
      {/* 논문 트렌드 섹션 (전체 너비) */}
      <Box sx={{ mb: 4 }}>
        {renderTrendSection()}
      </Box>
      
      {/* 2열 그리드 레이아웃 */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
        gap: 3 
      }}>
        {sections.slice(1).map((section) => (
          <Box key={section.key}>
            {renderSection(section)}
          </Box>
        ))}
      </Box>
    </Box>
  );
}
