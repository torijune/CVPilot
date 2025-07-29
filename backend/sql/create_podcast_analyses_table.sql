-- 팟캐스트 분석 결과 테이블 생성
CREATE TABLE IF NOT EXISTS podcast_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    field TEXT NOT NULL,
    papers JSONB NOT NULL DEFAULT '[]',
    analysis_text TEXT NOT NULL,
    audio_file_path TEXT,
    duration_seconds INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_podcast_analyses_field ON podcast_analyses(field);
CREATE INDEX IF NOT EXISTS idx_podcast_analyses_created_at ON podcast_analyses(created_at);

-- RLS (Row Level Security) 활성화
ALTER TABLE podcast_analyses ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 읽기/쓰기 가능하도록 정책 설정
CREATE POLICY "Enable read access for all users" ON podcast_analyses
    FOR SELECT USING (true);

CREATE POLICY "Enable insert access for all users" ON podcast_analyses
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update access for all users" ON podcast_analyses
    FOR UPDATE USING (true);

CREATE POLICY "Enable delete access for all users" ON podcast_analyses
    FOR DELETE USING (true);

-- updated_at 자동 업데이트를 위한 트리거 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거 생성
CREATE TRIGGER update_podcast_analyses_updated_at 
    BEFORE UPDATE ON podcast_analyses 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column(); 