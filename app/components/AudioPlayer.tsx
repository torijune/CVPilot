import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Button,
  Slider,
  Typography,
  Paper,
  IconButton,
  LinearProgress,
} from '@mui/material';
import {
  PlayArrow as PlayArrowIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  VolumeUp as VolumeUpIcon,
  VolumeOff as VolumeOffIcon,
} from '@mui/icons-material';

interface AudioPlayerProps {
  audioUrl: string;
  title?: string;
  onClose?: () => void;
}

const AudioPlayer: React.FC<AudioPlayerProps> = ({ audioUrl, title, onClose }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    if (audioUrl) {
      // 상대 경로인 경우 백엔드 URL 추가
      const fullAudioUrl = audioUrl.startsWith('http') 
        ? audioUrl 
        : `${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}${audioUrl}`;
      
      const audio = new Audio(fullAudioUrl);
      audioRef.current = audio;

      // 이벤트 리스너 설정
      audio.addEventListener('loadedmetadata', () => {
        setDuration(audio.duration);
        setIsLoading(false);
      });

      audio.addEventListener('timeupdate', () => {
        setCurrentTime(audio.currentTime);
      });

      audio.addEventListener('ended', () => {
        setIsPlaying(false);
        setCurrentTime(0);
      });

      audio.addEventListener('error', (e) => {
        console.error('오디오 로드 오류:', e);
        setError('오디오 파일을 로드할 수 없습니다.');
        setIsLoading(false);
      });

      audio.addEventListener('canplay', () => {
        setIsLoading(false);
      });

      // 컴포넌트 언마운트 시 정리
      return () => {
        if (audioRef.current) {
          audioRef.current.pause();
          audioRef.current = null;
        }
      };
    }
  }, [audioUrl]);

  const handlePlayPause = () => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play().catch((error) => {
        console.error('오디오 재생 실패:', error);
        setError('오디오 재생에 실패했습니다.');
      });
      setIsPlaying(true);
    }
  };

  const handleStop = () => {
    if (!audioRef.current) return;
    
    audioRef.current.pause();
    audioRef.current.currentTime = 0;
    setIsPlaying(false);
    setCurrentTime(0);
  };

  const handleSeek = (event: Event, newValue: number | number[]) => {
    if (!audioRef.current) return;
    
    const newTime = newValue as number;
    audioRef.current.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const handleVolumeChange = (event: Event, newValue: number | number[]) => {
    if (!audioRef.current) return;
    
    const newVolume = newValue as number;
    setVolume(newVolume);
    audioRef.current.volume = newVolume;
    
    if (newVolume === 0) {
      setIsMuted(true);
    } else if (isMuted) {
      setIsMuted(false);
    }
  };

  const handleMuteToggle = () => {
    if (!audioRef.current) return;
    
    if (isMuted) {
      audioRef.current.volume = volume;
      setIsMuted(false);
    } else {
      audioRef.current.volume = 0;
      setIsMuted(true);
    }
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  if (error) {
    return (
      <Paper elevation={3} sx={{ p: 3, m: 2 }}>
        <Typography color="error" variant="h6" gutterBottom>
          오류 발생
        </Typography>
        <Typography color="error">{error}</Typography>
        <Button onClick={onClose} sx={{ mt: 2 }}>
          닫기
        </Button>
      </Paper>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3, m: 2, maxWidth: 600 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          {title || '오디오 재생'}
        </Typography>
        {onClose && (
          <Button onClick={onClose} size="small">
            닫기
          </Button>
        )}
      </Box>

      {isLoading && (
        <Box sx={{ mb: 2 }}>
          <LinearProgress />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            오디오 로딩 중...
          </Typography>
        </Box>
      )}

      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {formatTime(currentTime)} / {formatTime(duration)}
        </Typography>
        <Slider
          value={currentTime}
          max={duration}
          onChange={handleSeek}
          disabled={isLoading}
          sx={{ mb: 1 }}
        />
      </Box>

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
        <IconButton onClick={handlePlayPause} disabled={isLoading}>
          {isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
        </IconButton>
        <IconButton onClick={handleStop} disabled={isLoading}>
          <StopIcon />
        </IconButton>
        
        <Box sx={{ display: 'flex', alignItems: 'center', ml: 'auto' }}>
          <IconButton onClick={handleMuteToggle} disabled={isLoading}>
            {isMuted ? <VolumeOffIcon /> : <VolumeUpIcon />}
          </IconButton>
          <Slider
            value={isMuted ? 0 : volume}
            min={0}
            max={1}
            step={0.1}
            onChange={handleVolumeChange}
            disabled={isLoading}
            sx={{ width: 100, ml: 1 }}
          />
        </Box>
      </Box>

      <Typography variant="body2" color="text.secondary">
        {isPlaying ? '재생 중...' : '일시정지됨'}
      </Typography>
    </Paper>
  );
};

export default AudioPlayer; 