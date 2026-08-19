# Artha AI

> AI-powered multilingual dataset generation platform for Indian languages

Generate production-ready labeled datasets in **Hindi, Gujarati, Tamil, Marathi, Bengali, Telugu, Kannada** and more. Get sentiment, intent, or toxicity labels in minutes - ready for ML training.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)

---

## 🎯 Features

- **8+ Indian Languages** - Hindi, Gujarati, Tamil, Marathi, Bengali, Telugu, Kannada, English
- **3 Label Types** - Sentiment, Intent, Toxicity detection
- **Multi-Source Scraping** - Reddit, YouTube, Google Play, News
- **AI-Powered Labeling** - Using Groq, OpenRouter, Claude, GPT
- **Quality Assurance** - Automatic quality scoring and balance checks
- **Multiple Export Formats** - CSV, JSON, Excel, Parquet, HuggingFace
- **Real-time Progress** - Live tracking of dataset generation
- **User Authentication** - Secure JWT-based auth system

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL database (Supabase recommended)
- Redis instance (Upstash recommended)
- LLM API key (Groq/OpenRouter/Claude/GPT)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Parshva2605/Artha.ai.git
cd Artha.ai
```

2. **Set up backend**
```bash
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env
# Edit .env with your API keys
```

3. **Set up frontend**
```bash
cd ../frontend
npm install
```

4. **Start with Docker (Recommended)**
```bash
docker compose up --build
```

Or start services individually:
```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload

# Terminal 2: Worker
cd backend
celery -A workers.celery_app.celery_app worker -l info --pool=solo

# Terminal 3: Frontend
cd frontend
npm run dev
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📖 Documentation

- **[Setup Guide](LOCAL_SETUP.md)** - Detailed installation and configuration
- **[Project Info](info.md)** - Architecture and technical details
- **[API Documentation](http://localhost:8000/docs)** - Interactive API reference

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Next.js UI     │  User Interface
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI        │  REST API
└────────┬────────┘
         │
         ├──► PostgreSQL (Supabase)   - Data storage
         ├──► Redis (Upstash)          - Task queue
         └──► Celery Worker            - Background jobs
                  │
                  ├──► Scrapers        - Data collection
                  ├──► Pipeline        - Processing
                  └──► LLM APIs        - Labeling
```

---

## 🛠️ Tech Stack

**Frontend:**
- Next.js 14
- React 18
- TypeScript
- TailwindCSS
- TanStack Query

**Backend:**
- FastAPI
- Celery
- SQLAlchemy
- Pydantic v2

**Infrastructure:**
- PostgreSQL (Supabase)
- Redis (Upstash)
- Docker

**AI/ML:**
- Groq
- OpenRouter
- Anthropic Claude
- OpenAI GPT

---

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/db

# Redis
REDIS_URL=rediss://your-redis-url

# LLM APIs (at least one required)
GROQ_API_KEY=your-groq-key
OPENROUTER_API_KEY=your-openrouter-key

# Authentication
JWT_SECRET_KEY=your-secret-key-min-32-chars

# URLs
FRONTEND_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

See `.env.example` for complete list.

---

## 📊 Usage

### Generate a Dataset

1. **Select Languages** - Choose one or more Indian languages
2. **Choose Label Type** - Sentiment, Intent, or Toxicity
3. **Set Quantity** - Rows per language (10-500)
4. **Select Export Formats** - CSV, JSON, Excel, Parquet, or HuggingFace
5. **Generate** - Wait 2-10 minutes
6. **Download** - Get your labeled dataset

### API Usage

```python
import requests

# Generate dataset
response = requests.post('http://localhost:8000/api/generate-dataset', json={
    "languages": ["hi", "gu"],
    "quantity_per_language": 100,
    "label_type": "sentiment",
    "export_formats": ["csv", "json"]
})

job_id = response.json()['job_id']

# Check status
status = requests.get(f'http://localhost:8000/api/job-status/{job_id}')
print(status.json())
```

---

## 🚢 Deployment

### Backend (Railway/Render)

1. Create new service from GitHub
2. Set root directory: `backend`
3. Add environment variables
4. Deploy

### Frontend (Vercel)

1. Import GitHub repository
2. Set root directory: `frontend`
3. Add `NEXT_PUBLIC_API_URL` environment variable
4. Deploy

### Database (Supabase)

1. Create new project
2. Copy PostgreSQL connection string
3. Add to `DATABASE_URL` environment variable

### Redis (Upstash)

1. Create Redis database
2. Copy connection string
3. Add to `REDIS_URL` environment variable

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built for the Indian AI ecosystem
- Supports low-resource Indian languages
- Powered by open-source LLMs

---

## 📧 Contact

Parshva Shah - [@Parshva2605](https://github.com/Parshva2605)

Project Link: [https://github.com/Parshva2605/Artha.ai](https://github.com/Parshva2605/Artha.ai)

---

**Made with ❤️ for Indian Language AI**

