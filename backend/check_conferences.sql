-- 1. 전체 학회별 논문 수 (상위 20개)
SELECT 
    conference,
    COUNT(*) as paper_count,
    MIN(year) as earliest_year,
    MAX(year) as latest_year
FROM papers 
WHERE conference IS NOT NULL 
    AND conference != ''
GROUP BY conference
ORDER BY paper_count DESC
LIMIT 20;

-- 2. 분야별 학회 분포
SELECT 
    field,
    conference,
    COUNT(*) as paper_count
FROM papers 
WHERE conference IS NOT NULL 
    AND conference != ''
    AND field IS NOT NULL
GROUP BY field, conference
ORDER BY field, paper_count DESC;

-- 3. ML/DL 분야의 학회별 분포
SELECT 
    conference,
    COUNT(*) as paper_count,
    MIN(year) as earliest_year,
    MAX(year) as latest_year,
    ARRAY_AGG(DISTINCT year ORDER BY year) as years
FROM papers 
WHERE field = 'Machine Learning / Deep Learning (ML/DL)'
    AND conference IS NOT NULL 
    AND conference != ''
GROUP BY conference
ORDER BY paper_count DESC;

-- 4. ICLR 관련 상세 정보
SELECT 
    field,
    conference,
    year,
    COUNT(*) as paper_count
FROM papers 
WHERE conference ILIKE '%ICLR%'
GROUP BY field, conference, year
ORDER BY year DESC, paper_count DESC;

-- 5. 각 분야별 총 논문 수
SELECT 
    field,
    COUNT(*) as total_papers,
    COUNT(DISTINCT conference) as unique_conferences
FROM papers 
WHERE field IS NOT NULL
GROUP BY field
ORDER BY total_papers DESC;

-- 6. 연도별 학회 분포 (최근 3년)
SELECT 
    year,
    conference,
    COUNT(*) as paper_count
FROM papers 
WHERE year >= 2022
    AND conference IS NOT NULL 
    AND conference != ''
GROUP BY year, conference
HAVING COUNT(*) >= 10  -- 10개 이상인 경우만
ORDER BY year DESC, paper_count DESC; 