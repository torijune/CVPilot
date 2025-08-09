import React, { useState } from "react";
import { Box } from "@mui/material";
import Sidebar from "../components/Sidebar";
import AnalysisPanel from "../components/AnalysisPanel";
import { analyzeCV, extractTextFromFile } from "../api/cv-analysis";
import { getPaperTrend } from "../api/trends";

export default function Dashboard() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sidebarWidth, setSidebarWidth] = useState(380);

  const handleAnalyze = async (cvFile: File | null, interests: string[]) => {
    if (!cvFile || interests.length === 0) {
      setError("CV 파일과 관심 분야를 모두 선택해주세요.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // 1. CV 파일에서 텍스트 추출
      const cvText = await extractTextFromFile(cvFile);
      
      // 2. 관심 분야를 주요 분야와 세부 분야로 구분
      const mainInterests = [
        "Natural Language Processing (NLP)",
        "Computer Vision (CV)",
        "Multimodal",
        "Machine Learning / Deep Learning (ML/DL)"
      ];
      
      const mainInterest = interests.find(interest => mainInterests.includes(interest)) || interests[0];
      const detailedInterests = interests.filter(interest => !mainInterests.includes(interest));
      
      // 3. CV 분석 수행
      const cvAnalysisResult = await analyzeCV(cvText, mainInterest);
      
      // 4. 논문 트렌드 조회 (주요 분야와 세부 분야 모두 전달)
      const paperTrendResult = await getPaperTrend(mainInterest, detailedInterests, 10);
      
      // 5. 결과 통합
      setResult({
        trend: cvAnalysisResult.trend,
        professors: cvAnalysisResult.professors,
        feedback: cvAnalysisResult.feedback,
        improvement: cvAnalysisResult.improvement,
        project: cvAnalysisResult.project,
        paperTrend: paperTrendResult.trend_summary,
        analysis_details: paperTrendResult.analysis_details,
        papers: paperTrendResult.papers,
      });
      
    } catch (err) {
      console.error("분석 중 오류 발생:", err);
      setError(err instanceof Error ? err.message : "분석 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const handleSidebarWidthChange = (width: number) => {
    setSidebarWidth(width);
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      height: '100vh', 
      overflow: 'hidden',
      background: 'linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%)'
    }}>
      {/* 사이드바 */}
      <Box sx={{ 
        flexShrink: 0,
        zIndex: 10,
        boxShadow: '4px 0 20px rgba(0, 0, 0, 0.1)'
      }}>
        <Sidebar 
          onAnalyze={handleAnalyze} 
          loading={loading} 
          onWidthChange={handleSidebarWidthChange}
        />
      </Box>
      
      {/* 메인 콘텐츠 영역 */}
      <Box sx={{ 
        flex: 1, 
        overflow: 'hidden',
        transition: 'all 0.3s ease',
        position: 'relative'
      }}>
        <AnalysisPanel 
          result={result} 
          error={error} 
        />
      </Box>
    </Box>
  );
} 