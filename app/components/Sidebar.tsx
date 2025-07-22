import React, { useState } from "react";
import { Drawer, Box, Typography, Button } from "@mui/material";
import CVUploader from "./CVUploader";
import InterestSelector from "./InterestSelector";

type Props = {
  onAnalyze: (cvFile: File | null, interests: string[]) => void;
  loading: boolean;
};

const Sidebar: React.FC<Props> = ({ onAnalyze, loading }) => {
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [interests, setInterests] = useState<string[]>([]);

  return (
    <Drawer variant="permanent" anchor="left" PaperProps={{ sx: { width: 300, p: 2 } }}>
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>관심 분야 & CV 업로드</Typography>
        <InterestSelector value={interests} onChange={setInterests} />
        <CVUploader onFileChange={setCvFile} />
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
    </Drawer>
  );
};

export default Sidebar;
