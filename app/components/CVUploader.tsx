import React from "react";
import { Button, Box, Typography } from "@mui/material";
import UploadFileIcon from "@mui/icons-material/UploadFile";

type Props = {
  onFileChange: (file: File | null) => void;
};

const CVUploader: React.FC<Props> = ({ onFileChange }) => (
  <Box my={2}>
    <Typography variant="subtitle1" gutterBottom>
      CV 파일 업로드 (pdf, doc, docx)
    </Typography>
    <Button
      variant="contained"
      component="label"
      startIcon={<UploadFileIcon />}
    >
      파일 선택
      <input
        type="file"
        accept=".pdf,.doc,.docx"
        hidden
        onChange={e => onFileChange(e.target.files?.[0] || null)}
      />
    </Button>
  </Box>
);

export default CVUploader;
