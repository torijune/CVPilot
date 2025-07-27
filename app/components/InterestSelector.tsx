import React, { useState } from "react";
import { 
  Box,
  Typography,
  Chip,
  TextField,
  IconButton
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";

const INTERESTS = [
  "Natural Language Processing (NLP)",
  "Computer Vision (CV)",
  "Multimodal",
  "Machine Learning / Deep Learning (ML/DL)"
];

type Props = {
  value: string[];
  onChange: (v: string[]) => void;
};

const InterestSelector: React.FC<Props> = ({ value, onChange }) => {
  const [customInterest, setCustomInterest] = useState("");

  const handleAddCustomInterest = () => {
    const trimmed = customInterest.trim();
    
    if (!trimmed || value.includes(trimmed) || trimmed.length > 50) {
      return;
    }
    
    onChange([...value, trimmed]);
    setCustomInterest("");
  };

  const handleRemoveInterest = (interestToRemove: string) => {
    onChange(value.filter(interest => interest !== interestToRemove));
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      handleAddCustomInterest();
    }
  };

  const handleInterestToggle = (interest: string) => {
    if (value.includes(interest)) {
      handleRemoveInterest(interest);
    } else {
      onChange([...value, interest]);
    }
  };

  return (
    <Box sx={{ mb: 4 }}>
      {/* 제목 */}
      <Typography 
        variant="h6" 
        sx={{ 
          mb: 3, 
          fontWeight: 700, 
          color: '#FFFFFF',
          fontSize: '1.25rem'
        }}
      >
        관심 분야
      </Typography>

      {/* 주요 관심 분야 */}
      <Box sx={{ mb: 3 }}>
        <Typography 
          variant="subtitle1" 
          sx={{ 
            mb: 2, 
            color: '#E5E7EB', 
            fontWeight: 600,
            fontSize: '1rem'
          }}
        >
          주요 분야
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5 }}>
          {INTERESTS.map((interest) => (
            <Chip
              key={interest}
              label={interest}
              onClick={() => handleInterestToggle(interest)}
              sx={{
                backgroundColor: value.includes(interest) 
                  ? 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)' 
                  : 'rgba(255, 255, 255, 0.1)',
                color: value.includes(interest) ? '#FFFFFF' : '#E5E7EB',
                fontWeight: 600,
                fontSize: '0.875rem',
                padding: '8px 16px',
                borderRadius: 3,
                border: value.includes(interest) ? 'none' : '1px solid rgba(255, 255, 255, 0.2)',
                '&:hover': {
                  backgroundColor: value.includes(interest) 
                    ? 'linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%)' 
                    : 'rgba(255, 255, 255, 0.2)',
                  transform: 'translateY(-1px)',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
                },
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                backdropFilter: 'blur(10px)'
              }}
            />
          ))}
        </Box>
      </Box>

      {/* 세부 관심 분야 입력 */}
      <Box sx={{ mb: 3 }}>
        <Typography 
          variant="subtitle1" 
          sx={{ 
            mb: 2, 
            color: '#E5E7EB', 
            fontWeight: 600,
            fontSize: '1rem'
          }}
        >
          세부 분야 추가
        </Typography>
        <Box sx={{ display: 'flex', gap: 1.5 }}>
          <TextField
            fullWidth
            size="small"
            placeholder="예: Transformer, GAN, Reinforcement Learning"
            value={customInterest}
            onChange={(e) => setCustomInterest(e.target.value)}
            onKeyPress={handleKeyPress}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 3,
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                '& fieldset': {
                  border: 'none',
                },
                '&:hover fieldset': {
                  border: 'none',
                },
                '&.Mui-focused fieldset': {
                  border: '2px solid #3B82F6',
                },
                '& input': {
                  color: '#FFFFFF',
                  '&::placeholder': {
                    color: '#9CA3AF',
                    opacity: 1
                  }
                }
              }
            }}
          />
          <IconButton
            onClick={handleAddCustomInterest}
            disabled={!customInterest.trim() || value.includes(customInterest.trim())}
            sx={{
              backgroundColor: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
              color: 'white',
              borderRadius: 3,
              width: 48,
              height: 48,
              boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)',
              '&:hover': {
                backgroundColor: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                transform: 'translateY(-1px)',
                boxShadow: '0 6px 16px rgba(16, 185, 129, 0.4)'
              },
              '&.Mui-disabled': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                color: '#9CA3AF',
                boxShadow: 'none',
                transform: 'none'
              }
            }}
          >
            <AddIcon />
          </IconButton>
        </Box>
      </Box>

      {/* 선택된 관심 분야 표시 */}
      {value.length > 0 && (
        <Box>
          <Typography 
            variant="subtitle1" 
            sx={{ 
              mb: 2, 
              color: '#E5E7EB', 
              fontWeight: 600,
              fontSize: '1rem'
            }}
          >
            선택된 분야 ({value.length}개)
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5 }}>
            {value.map((interest) => (
              <Chip
                key={interest}
                label={interest}
                onDelete={() => handleRemoveInterest(interest)}
                sx={{
                  backgroundColor: INTERESTS.includes(interest) 
                    ? 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)' 
                    : 'rgba(16, 185, 129, 0.2)',
                  color: INTERESTS.includes(interest) ? '#FFFFFF' : '#10B981',
                  fontWeight: 600,
                  fontSize: '0.875rem',
                  padding: '8px 16px',
                  borderRadius: 3,
                  border: INTERESTS.includes(interest) ? 'none' : '1px solid rgba(16, 185, 129, 0.3)',
                  '& .MuiChip-deleteIcon': {
                    color: INTERESTS.includes(interest) ? '#FFFFFF' : '#10B981',
                    '&:hover': {
                      color: INTERESTS.includes(interest) ? '#E5E7EB' : '#059669',
                    }
                  },
                  '&:hover': {
                    transform: 'translateY(-1px)',
                    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
                  },
                  transition: 'all 0.2s ease'
                }}
              />
            ))}
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default InterestSelector;
