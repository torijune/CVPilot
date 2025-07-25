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
    <Box sx={{ mb: 3 }}>
      {/* 제목 */}
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: '#1a1a1a' }}>
        관심 분야
      </Typography>

      {/* 주요 관심 분야 */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" sx={{ mb: 1.5, color: '#666', fontWeight: 500 }}>
          주요 분야
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {INTERESTS.map((interest) => (
            <Chip
              key={interest}
              label={interest}
              onClick={() => handleInterestToggle(interest)}
              sx={{
                backgroundColor: value.includes(interest) ? '#3182f6' : '#f5f5f5',
                color: value.includes(interest) ? 'white' : '#333',
                fontWeight: 500,
                '&:hover': {
                  backgroundColor: value.includes(interest) ? '#1d4ed8' : '#e5e5e5',
                },
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
            />
          ))}
        </Box>
      </Box>

      {/* 세부 관심 분야 입력 (항상 표시) */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" sx={{ mb: 1.5, color: '#666', fontWeight: 500 }}>
          세부 분야 추가
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            size="small"
            placeholder="예: Transformer, GAN, Reinforcement Learning"
            value={customInterest}
            onChange={(e) => setCustomInterest(e.target.value)}
            onKeyPress={handleKeyPress}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
                '& fieldset': {
                  borderColor: '#e0e0e0',
                },
                '&:hover fieldset': {
                  borderColor: '#bdbdbd',
                },
              }
            }}
          />
          <IconButton
            onClick={handleAddCustomInterest}
            disabled={!customInterest.trim() || value.includes(customInterest.trim())}
            sx={{
              backgroundColor: '#3182f6',
              color: 'white',
              '&:hover': {
                backgroundColor: '#1d4ed8',
              },
              '&.Mui-disabled': {
                backgroundColor: '#e0e0e0',
                color: '#999',
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
          <Typography variant="body2" sx={{ mb: 1.5, color: '#666', fontWeight: 500 }}>
            선택된 분야 ({value.length}개)
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {value.map((interest) => (
              <Chip
                key={interest}
                label={interest}
                onDelete={() => handleRemoveInterest(interest)}
                sx={{
                  backgroundColor: INTERESTS.includes(interest) ? '#3182f6' : '#f0f8ff',
                  color: INTERESTS.includes(interest) ? 'white' : '#3182f6',
                  fontWeight: 500,
                  '& .MuiChip-deleteIcon': {
                    color: INTERESTS.includes(interest) ? 'white' : '#3182f6',
                    '&:hover': {
                      color: INTERESTS.includes(interest) ? '#e0e0e0' : '#1d4ed8',
                    }
                  }
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
