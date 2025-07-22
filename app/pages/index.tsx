import React, { useState } from "react";
import Sidebar from "../components/Sidebar";
import AnalysisPanel from "../components/AnalysisPanel";

export default function Dashboard() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async (cvFile: File | null, interests: string[]) => {
    if (!cvFile || interests.length === 0) return;
    setLoading(true);
    // 실제 API 연동
    const formData = new FormData();
    formData.append("cv", cvFile);
    formData.append("interests", interests.join(","));
    const res = await fetch("/api/v1/user/cv", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    setResult({
      summary: data.summary,
      feedback: data.suggestions,
      trend: data.trend, // 논문 트렌드 결과
      professors: data.professors, // 교수/대학원 리스트
      project: data.projects,
    });
    setLoading(false);
  };

  return (
    <div>
      <Sidebar onAnalyze={handleAnalyze} loading={loading} />
      <AnalysisPanel result={result} />
    </div>
  );
}
