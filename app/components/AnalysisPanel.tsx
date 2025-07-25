import React from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Paper from "@mui/material/Paper";
import Divider from "@mui/material/Divider";
import Avatar from "@mui/material/Avatar";
import Chip from "@mui/material/Chip";
import Link from "@mui/material/Link";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import SchoolIcon from "@mui/icons-material/School";
import FeedbackIcon from "@mui/icons-material/Feedback";
import TipsAndUpdatesIcon from "@mui/icons-material/TipsAndUpdates";
import AssignmentIcon from "@mui/icons-material/Assignment";

const sections = [
  {
    key: "trend",
    label: "논문 트렌드",
    icon: <TrendingUpIcon sx={{ bgcolor: '#43a047', color: 'white', p: 1, borderRadius: 1 }} />, 
    color: "#e8f5e9"
  },
  {
    key: "professors",
    label: "교수/대학원",
    icon: <SchoolIcon sx={{ bgcolor: '#0288d1', color: 'white', p: 1, borderRadius: 1 }} />, 
    color: "#e1f5fe"
  },
  {
    key: "feedback",
    label: "CV 피드백",
    icon: <FeedbackIcon sx={{ bgcolor: '#ff9800', color: 'white', p: 1, borderRadius: 1 }} />, 
    color: "#fff3e0"
  },
  {
    key: "improvement",
    label: "개선 방향",
    icon: <TipsAndUpdatesIcon sx={{ bgcolor: '#ffd600', color: 'white', p: 1, borderRadius: 1 }} />, 
    color: "#fffde7"
  },
  {
    key: "project",
    label: "프로젝트 가이드",
    icon: <AssignmentIcon sx={{ bgcolor: '#7b1fa2', color: 'white', p: 1, borderRadius: 1 }} />, 
    color: "#f3e5f5"
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
            p: 3,
            background: '#ffebee',
            boxShadow: 2,
            borderRadius: 1,
            border: '1px solid #f44336',
            maxWidth: 600,
            width: '100%'
          }}
        >
          <Typography variant="h6" color="error" sx={{ fontWeight: 700, mb: 1 }}>
            분석 중 오류가 발생했습니다
          </Typography>
          <Typography color="error" sx={{ whiteSpace: 'pre-line' }}>
            {error}
          </Typography>
        </Paper>
      </Box>
    );
  }

  const renderTrendSection = () => {
    const trendText = result?.trend || "논문 트렌드 결과가 여기에 표시됩니다.";
    const papers = result?.papers || [];
    
    return (
      <Paper
        sx={{
          p: 2.5,
          minHeight: 110,
          background: "#e8f5e9",
          boxShadow: 2,
          borderRadius: 1,
          mb: 2.5,
          width: '100%',
          maxWidth: '100%',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
          <Avatar sx={{ bgcolor: 'transparent', mr: 1, width: 36, height: 36 }}>
            <TrendingUpIcon sx={{ bgcolor: '#43a047', color: 'white', p: 1, borderRadius: 1 }} />
          </Avatar>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>논문 트렌드</Typography>
        </Box>
        <Divider sx={{ mb: 1.5 }} />
        
        {/* 트렌드 요약 */}
        <Typography sx={{ whiteSpace: 'pre-line', color: '#333', fontSize: 16, mb: 2 }}>
          {trendText}
        </Typography>
        
        {/* 관련 논문 목록 */}
        {papers.length > 0 && (
          <Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#2e7d32' }}>
              관련 논문 ({papers.length}개)
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {papers.slice(0, 5).map((paper: any, index: number) => (
                <Box key={index} sx={{ 
                  p: 1.5, 
                  border: '1px solid #c8e6c9', 
                  borderRadius: 1, 
                  backgroundColor: 'white' 
                }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 0.5 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#1b5e20', flex: 1 }}>
                      {paper.title}
                    </Typography>
                    <Chip 
                      label={`${paper.conference} ${paper.year}`} 
                      size="small" 
                      sx={{ 
                        backgroundColor: '#4caf50', 
                        color: 'white', 
                        fontSize: '0.7rem',
                        ml: 1
                      }} 
                    />
                  </Box>
                  {paper.url && (
                    <Link 
                      href={paper.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      sx={{ 
                        fontSize: '0.8rem', 
                        color: '#1976d2',
                        textDecoration: 'none',
                        '&:hover': { textDecoration: 'underline' }
                      }}
                    >
                      논문 보기 →
                    </Link>
                  )}
                </Box>
              ))}
            </Box>
          </Box>
        )}
      </Paper>
    );
  };

  return (
    <Box sx={{ 
      p: 3, 
      height: '100%',
      overflow: 'auto'
    }}>
      {/* 논문 트렌드 섹션 (커스텀 렌더링) */}
      {renderTrendSection()}
      
      {/* 나머지 섹션들 */}
      {sections.slice(1).map((section) => (
        <Paper
          key={section.key}
          sx={{
            p: 2.5,
            minHeight: 110,
            background: section.color,
            boxShadow: 2,
            borderRadius: 1,
            mb: 2.5,
            width: '100%',
            maxWidth: '100%',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
            <Avatar sx={{ bgcolor: 'transparent', mr: 1, width: 36, height: 36 }}>
              {section.icon}
            </Avatar>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>{section.label}</Typography>
          </Box>
          <Divider sx={{ mb: 1.5 }} />
          <Typography sx={{ whiteSpace: 'pre-line', color: '#333', fontSize: 16 }}>
            {result?.[section.key] || `${section.label} 결과가 여기에 표시됩니다.`}
          </Typography>
        </Paper>
      ))}
    </Box>
  );
}
