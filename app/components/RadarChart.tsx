import React from 'react';
import {
  Radar,
  RadarChart as RechartsRadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip
} from 'recharts';
import { Box, Typography, Paper } from '@mui/material';

interface RadarChartProps {
  data: any;
  title?: string;
}

const RadarChart: React.FC<RadarChartProps> = ({ data, title = "능력 평가" }) => {
  // 데이터 구조에 따라 적절한 형식으로 변환
  let chartData: any[] = [];
  
  if (data && data.radar_chart_data && data.radar_chart_data.scores) {
    // radar_chart_data.scores가 있는 경우
    chartData = Object.entries(data.radar_chart_data.scores).map(([category, score]) => ({
      category,
      score: Number(score),
      fullMark: 1
    }));
  } else if (data && data.scores) {
    // 직접 scores가 있는 경우
    chartData = Object.entries(data.scores).map(([category, score]) => ({
      category,
      score: Number(score),
      fullMark: 1
    }));
  } else if (data) {
    // 개별 점수들이 있는 경우
    const categories = [
      "연구 능력", "개발 스킬", "수상/성과", 
      "최신 기술 트렌드", "학술 배경", "프로젝트 경험"
    ];
    
    chartData = categories.map(category => {
      let score = 0;
      switch (category) {
        case "연구 능력":
          score = data.research_ability || 0;
          break;
        case "개발 스킬":
          score = data.development_skill || 0;
          break;
        case "수상/성과":
          score = data.awards_achievements || 0;
          break;
        case "최신 기술 트렌드":
          score = data.latest_tech_trend || 0;
          break;
        case "학술 배경":
          score = data.academic_background || 0;
          break;
        case "프로젝트 경험":
          score = data.project_experience || 0;
          break;
      }
      return {
        category,
        score: Number(score),
        fullMark: 1
      };
    });
  }

  // 데이터가 없으면 빈 차트 표시
  if (chartData.length === 0) {
    return (
      <Paper elevation={2} sx={{ p: 3, height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          레이더 차트 데이터를 불러올 수 없습니다.
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={2} sx={{ p: 3, height: 400 }}>
      <Typography variant="h6" sx={{ mb: 2, textAlign: 'center' }}>
        {title}
      </Typography>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsRadarChart data={chartData}>
          <PolarGrid />
          <PolarAngleAxis dataKey="category" />
          <PolarRadiusAxis 
            angle={90} 
            domain={[0, 1]} 
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => `${Math.round(value * 100)}%`}
          />
          <Radar
            name="능력 점수"
            dataKey="score"
            stroke="#8884d8"
            fill="#8884d8"
            fillOpacity={0.3}
          />
          <Tooltip 
            formatter={(value: number) => [`${Math.round(value * 100)}%`, '능력 점수']}
            labelFormatter={(label) => `${label}`}
          />
        </RechartsRadarChart>
      </ResponsiveContainer>
    </Paper>
  );
};

export default RadarChart; 