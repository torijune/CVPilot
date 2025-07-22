import React from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Paper from "@mui/material/Paper";
import Divider from "@mui/material/Divider";
import Avatar from "@mui/material/Avatar";
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
};

export default function AnalysisPanel({ result }: Props) {
  return (
    <Box sx={{ ml: 38, p: 2, maxWidth: '1200px', margin: '0 auto' }}>
      {sections.map((section) => (
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
