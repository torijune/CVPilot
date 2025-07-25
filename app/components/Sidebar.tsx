import React, { useState, useRef, useEffect } from "react";
import { Box, Typography, Button, Paper } from "@mui/material";
import CVUploader from "./CVUploader";
import InterestSelector from "./InterestSelector";

type Props = {
  onAnalyze: (cvFile: File | null, interests: string[]) => void;
  loading: boolean;
  onWidthChange?: (width: number) => void;
};

const Sidebar: React.FC<Props> = ({ onAnalyze, loading, onWidthChange }) => {
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [interests, setInterests] = useState<string[]>([]);
  const [sidebarWidth, setSidebarWidth] = useState(320);
  const [isResizing, setIsResizing] = useState(false);
  const resizeRef = useRef<HTMLDivElement>(null);

  // 최소/최대 너비 설정
  const MIN_WIDTH = 280;
  const MAX_WIDTH = 500;

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;

      const newWidth = e.clientX;
      if (newWidth >= MIN_WIDTH && newWidth <= MAX_WIDTH) {
        setSidebarWidth(newWidth);
        onWidthChange?.(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing, onWidthChange]);

  const handleMouseDown = () => {
    setIsResizing(true);
  };

  return (
    <Box sx={{ position: 'relative', height: '100%' }}>
      {/* 사이드바 컨텐츠 */}
      <Paper
        elevation={2}
        sx={{
          width: sidebarWidth,
          height: '100%',
          borderRadius: 0,
          display: 'flex',
          flexDirection: 'column',
          transition: isResizing ? 'none' : 'width 0.2s ease',
          overflow: 'hidden'
        }}
      >
        <Box sx={{ 
          p: 3, 
          height: '100%', 
          overflow: 'auto',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <Typography variant="h6" sx={{ mb: 3, fontWeight: 600, color: '#1a1a1a' }}>
            관심 분야 & CV 업로드
          </Typography>
          
          <Box sx={{ flex: 1 }}>
            <InterestSelector value={interests} onChange={setInterests} />
            <CVUploader onFileChange={setCvFile} />
          </Box>
          
          <Button
            variant="contained"
            color="primary"
            fullWidth
            sx={{ mt: 2 }}
            disabled={!cvFile || interests.length === 0 || loading}
            onClick={() => onAnalyze(cvFile, interests)}
          >
            {loading ? "분석 중..." : "분석 시작"}
          </Button>
        </Box>
      </Paper>
      
      {/* 리사이즈 핸들 */}
      <Box
        ref={resizeRef}
        onMouseDown={handleMouseDown}
        sx={{
          position: 'absolute',
          right: -2,
          top: 0,
          width: 4,
          height: '100%',
          cursor: 'col-resize',
          backgroundColor: 'transparent',
          zIndex: 10,
          '&:hover': {
            backgroundColor: 'rgba(49, 130, 246, 0.1)',
          },
          '&::after': {
            content: '""',
            position: 'absolute',
            left: '50%',
            top: '50%',
            transform: 'translate(-50%, -50%)',
            width: 2,
            height: 40,
            backgroundColor: '#e0e0e0',
            borderRadius: 1,
            opacity: 0,
            transition: 'opacity 0.2s ease',
          },
          '&:hover::after': {
            opacity: 1,
          },
        }}
      />
    </Box>
  );
};

export default Sidebar;
