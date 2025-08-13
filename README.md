# CVPilot

AI-powered academic career analysis service

## Overview

CVPilot is an AI-based academic career analysis platform designed for students preparing for graduate school. It provides various features including CV analysis, paper trend analysis, interview practice, and more.

## Features

### 📊 CV Analysis
- AI-powered CV analysis with strengths and improvement suggestions
- Skill radar chart visualization
- Support for PDF, DOCX, and TXT files

### 📈 Paper Trend Analysis
- Real-time analysis of latest AI/ML research trends
- Hot topics identification by research field
- Keyword-based trend visualization

### 🔍 Paper Comparison Analysis
- Compare research ideas with existing papers
- Differentiation strategy suggestions
- Similarity analysis

### 💬 CV-based Interview Practice
- Interviewer mode: AI acts as an interviewer
- Practice mode: Sample answers and advice
- Customized question generation

### 🎙️ Daily Paper Podcast
- Audio summaries of latest papers
- TTS technology integration
- Audio player with controls

### 🏫 Lab Analysis
- Research field analysis by laboratory
- Faculty profile information
- Lab recommendations

## Tech Stack

### Frontend
- Next.js 14
- TypeScript
- Material-UI
- React Hooks

### Backend
- FastAPI
- Python 3.11
- AWS Lambda
- Docker

### AI/ML
- OpenAI GPT-4
- OpenAI Embedding API
- Supabase (PostgreSQL)

### Infrastructure
- AWS S3 (Static Hosting)
- AWS CloudFront (CDN)
- AWS ECR (Docker Registry)

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- OpenAI API Key

### Frontend Setup
```bash
cd app
npm install
npm run dev
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Deployment

### Frontend Deployment
```bash
cd app
./deploy-frontend.sh
```

### Backend Deployment
```bash
cd backend
./deploy-lambda.sh
```

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=https://your-lambda-url.amazonaws.com
```

### Backend (.env)
```
OPENAI_API_KEY=your-openai-api-key
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

## Project Structure

```
CVPilot/
├── app/                    # Frontend (Next.js)
│   ├── components/         # React components
│   ├── pages/             # Page components
│   ├── hooks/             # Custom Hooks
│   ├── api/               # API clients
│   └── config/            # Configuration files
├── backend/               # Backend (FastAPI)
│   ├── app/               # Main application
│   │   ├── cv_analysis/   # CV analysis module
│   │   ├── paper_trend/   # Paper trend module
│   │   ├── cv_QA/         # CV QA module
│   │   └── shared/        # Shared modules
│   └── requirements.txt   # Python dependencies
└── utils/                 # Utility scripts
```

## License

MIT License

## Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

<sub>Project Owner: WonJune Jang</sub>