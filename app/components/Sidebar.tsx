import React, { useState, useRef, useEffect } from "react";
import { Box, Typography, Button, Paper, useTheme } from "@mui/material";
import { useRouter } from "next/router";
import CVUploader from "./CVUploader";
import InterestSelector from "./InterestSelector";
import FlightTakeoffIcon from "@mui/icons-material/FlightTakeoff";
import HomeIcon from "@mui/icons-material/Home";

type Props = {
  onAnalyze: (cvFile: File | null, interests: string[]) => void;
  loading: boolean;
  onWidthChange?: (width: number) => void;
};

const Sidebar: React.FC<Props> = ({ onAnalyze, loading, onWidthChange }) => {
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [interests, setInterests] = useState<string[]>([]);
  const [sidebarWidth, setSidebarWidth] = useState(380);
  const [isResizing, setIsResizing] = useState(false);
  const resizeRef = useRef<HTMLDivElement>(null);
  const theme = useTheme();
  const router = useRouter();

  // 최소/최대 너비 설정
  const MIN_WIDTH = 320;
  const MAX_WIDTH = 600;

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
        elevation={0}
        sx={{
          width: sidebarWidth,
          height: '100%',
          borderRadius: 0,
          display: 'flex',
          flexDirection: 'column',
          transition: isResizing ? 'none' : 'width 0.2s ease',
          overflow: 'hidden',
          background: 'linear-gradient(180deg, #1F2937 0%, #374151 100%)',
          borderRight: '1px solid #E5E7EB'
        }}
      >
        <Box sx={{ 
          p: 3, 
          height: '100%', 
          overflow: 'auto',
          display: 'flex',
          flexDirection: 'column'
        }}>
          {/* CareerPilot 브랜드 로고 */}
          <Box sx={{ 
            mb: 4, 
            textAlign: 'center',
            pb: 3,
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              mb: 1
            }}>
              <FlightTakeoffIcon sx={{ 
                fontSize: 32, 
                color: '#3B82F6',
                mr: 1,
                filter: 'drop-shadow(0 2px 4px rgba(59, 130, 246, 0.3))'
              }} />
              <Typography 
                variant="h4" 
                sx={{ 
                  fontWeight: 800, 
                  background: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  fontSize: '1.75rem',
                  letterSpacing: '-0.025em'
                }}
              >
                CVPilot
              </Typography>
            </Box>
            <Typography 
              variant="body2" 
              sx={{ 
                color: '#9CA3AF',
                fontSize: '0.875rem',
                fontWeight: 500,
                letterSpacing: '0.025em'
              }}
            >
              AI-Powered Curriculum Vitae Advisor
            </Typography>
            
            {/* 홈페이지로 돌아가기 버튼 */}
            <Button
              variant="outlined"
              size="small"
              startIcon={<HomeIcon />}
              onClick={() => router.push('/')}
              sx={{
                mt: 2,
                borderColor: 'rgba(255, 255, 255, 0.3)',
                color: 'rgba(255, 255, 255, 0.8)',
                fontSize: '0.75rem',
                py: 0.5,
                px: 2,
                '&:hover': {
                  borderColor: 'rgba(255, 255, 255, 0.6)',
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  color: 'white'
                }
              }}
            >
              홈으로
            </Button>
          </Box>
          
          <Box sx={{ flex: 1 }}>
            <InterestSelector value={interests} onChange={setInterests} />
            <CVUploader onFileChange={setCvFile} />
          </Box>
          
          <Button
            variant="contained"
            fullWidth
            sx={{ 
              mt: 3,
              py: 2,
              fontSize: '1.1rem',
              fontWeight: 700,
              background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
              boxShadow: '0 4px 14px 0 rgba(16, 185, 129, 0.4)',
              '&:hover': {
                background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                boxShadow: '0 6px 20px 0 rgba(16, 185, 129, 0.5)',
                transform: 'translateY(-2px)'
              },
              '&:disabled': {
                background: '#6B7280',
                boxShadow: 'none',
                transform: 'none'
              }
            }}
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
            backgroundColor: 'rgba(59, 130, 246, 0.2)',
          },
          '&::after': {
            content: '""',
            position: 'absolute',
            left: '50%',
            top: '50%',
            transform: 'translate(-50%, -50%)',
            width: 2,
            height: 40,
            backgroundColor: '#E5E7EB',
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
