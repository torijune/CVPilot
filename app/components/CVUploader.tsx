import React, { useState, useRef } from "react";
import { 
  Button, 
  Box, 
  Typography, 
  Paper,
  IconButton
} from "@mui/material";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import DeleteIcon from "@mui/icons-material/Delete";

type Props = {
  onFileChange: (file: File | null) => void;
};

const CVUploader: React.FC<Props> = ({ onFileChange }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === "application/pdf" || 
          file.type === "application/msword" || 
          file.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document") {
        setSelectedFile(file);
        onFileChange(file);
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    if (file) {
      setSelectedFile(file);
      onFileChange(file);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    onFileChange(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Box>
      {!selectedFile ? (
        <Paper
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          sx={{
            p: 4,
            textAlign: 'center',
            backgroundColor: dragActive ? 'primary.50' : 'grey.50',
            border: dragActive 
              ? '2px dashed primary.main' 
              : '2px dashed grey.300',
            borderRadius: 2,
            transition: 'all 0.3s ease',
            cursor: 'pointer',
            '&:hover': {
              backgroundColor: 'primary.50',
              border: '2px dashed primary.main',
              transform: 'translateY(-2px)'
            }
          }}
          onClick={() => fileInputRef.current?.click()}
        >
          <CloudUploadIcon 
            sx={{ 
              fontSize: 48, 
              color: dragActive ? 'primary.main' : 'grey.500',
              mb: 2,
              transition: 'all 0.3s ease'
            }} 
          />
          <Typography 
            variant="h6" 
            sx={{ 
              mb: 1, 
              color: 'text.primary',
              fontWeight: 600
            }}
          >
            {dragActive ? '파일을 여기에 놓으세요' : '파일을 드래그하거나 클릭하세요'}
          </Typography>
          <Typography 
            variant="body2" 
            sx={{ 
              color: 'text.secondary',
              mb: 3
            }}
          >
            PDF, DOC, DOCX 파일 지원 (최대 10MB)
          </Typography>
          
          <Button
            variant="contained"
            component="label"
            startIcon={<UploadFileIcon />}
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
                transform: 'translateY(-1px)'
              }
            }}
          >
            파일 선택
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.doc,.docx"
              hidden
              onChange={handleFileSelect}
            />
          </Button>
        </Paper>
      ) : (
        <Paper
          sx={{
            p: 3,
            backgroundColor: 'success.50',
            border: '2px solid success.200',
            borderRadius: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <UploadFileIcon 
              sx={{ 
                fontSize: 32, 
                color: 'success.main',
                mr: 2
              }} 
            />
            <Box>
              <Typography 
                variant="subtitle1" 
                sx={{ 
                  color: 'text.primary',
                  fontWeight: 600,
                  mb: 0.5
                }}
              >
                {selectedFile.name}
              </Typography>
              <Typography 
                variant="body2" 
                sx={{ 
                  color: 'text.secondary'
                }}
              >
                {formatFileSize(selectedFile.size)}
              </Typography>
            </Box>
          </Box>
          
          <IconButton
            onClick={handleRemoveFile}
            sx={{
              backgroundColor: 'error.50',
              color: 'error.main',
              '&:hover': {
                backgroundColor: 'error.100',
                transform: 'scale(1.1)'
              }
            }}
          >
            <DeleteIcon />
          </IconButton>
        </Paper>
      )}
    </Box>
  );
};

export default CVUploader;
