import React from "react";
import { FormControl, InputLabel, Select, MenuItem, OutlinedInput, Chip, Box } from "@mui/material";

const INTERESTS = [
  "AI", "NLP", "CV", "Robotics", "Bioinformatics", "Data Science"
];

type Props = {
  value: string[];
  onChange: (v: string[]) => void;
};

const InterestSelector: React.FC<Props> = ({ value, onChange }) => (
  <Box my={2}>
    <FormControl fullWidth>
      <InputLabel>관심 분야</InputLabel>
      <Select
        multiple
        value={value}
        onChange={e => onChange(typeof e.target.value === 'string' ? e.target.value.split(',') : e.target.value)}
        input={<OutlinedInput label="관심 분야" />}
        renderValue={(selected) => (
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {(selected as string[]).map((val) => (
              <Chip key={val} label={val} />
            ))}
          </Box>
        )}
      >
        {INTERESTS.map(i => (
          <MenuItem key={i} value={i}>
            {i}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  </Box>
);

export default InterestSelector;
