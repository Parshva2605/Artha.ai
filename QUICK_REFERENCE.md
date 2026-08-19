# ⚡ Artha AI - Quick Reference Guide

## 🎯 **What Is This?**

**Artha AI** (formerly BhashaData) generates labeled datasets for Indian languages in 6 minutes or less.

**Input:** "Give me 100 Hindi sentiment-labeled sentences"  
**Output:** CSV/JSON/Excel with labeled data ready for ML training

---

## 📁 **Important Documentation Files**

| File | Purpose |
|------|---------|
| **PROJECT_FLOW.md** | Complete flow diagram (YOU ARE HERE) |
| **info.md** | Full technical handoff document |
| **README.md** | Basic setup and deployment guide |
| **LOCAL_SETUP.md** | Windows local development guide |
| **SETUP_COMPLETE.md** | Latest setup completion status |
| **INTEGRATION_TEST_REPORT.md** | Test results and verification |

---

## 🏃 **Quick Start Commands**

### **Run Backend + Worker Locally (Windows)**
```cmd
cd d:\pas\bhashaData\backend
start_local.bat
```

### **Run Frontend Locally**
```cmd
cd d:\pas\bhashaData\frontend
npm run dev
```

### **Run Everything with Docker**
```cmd
cd d:\pas\bhashaData
docker compose up --build
```

### **Check If Backend Is Running**
Open browser: http://localhost:8000/api/health

---

## 🔍 **Project Structure (Simplified)**

```
bhashaData/
├── backend/
│   ├── api/              # FastAPI routes, models, auth
│   ├── config/           # settings.py, languages.py
│   ├── database/         # SQLAlchemy models
│   ├── pipeline/         # cleaner, labeler, quality, exporter
│   ├── scrapers/         # reddit, youtube, google_play, news
│   ├── workers/          # Celery tasks
│   ├── main.py           # FastAPI app entry point
│   ├── .env.local        # Local environment variables
│   └── start_local.bat   # Windows startup script
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Landing page
│   │   ├── generate/          # Dataset generation form
│   │   ├── job/[id]/          # Progress tracking page
│   │   └── download/[id]/     # Download & quality report
│   ├── components/            # UI components
│   ├── lib/                   # API client, types
│   └── .env.local             # Frontend env (local)
│
├── datasets/                  # Generated datasets output
├── docker-compose.yml         # Full stack definition
├── .env                       # Production config (gitignored)
└── .env.example               # Template for environment vars
```

---

## 🔄 **The 6 Stages**

```
1. SCRAPING (15%)      → Collect from Reddit/YouTube/Play/News
2. CLEANING (35%)      → Remove noise, detect language, dedupe
3. LABELING (60%)      → AI labels (sentiment/intent/toxicity)
4. QUALITY CHECK (80%) → Validate confidence, balance
5. EXPORTING (92%)     → Generate CSV/JSON/Excel/Parquet
6. COMPLETE (100%)     → Ready to download
```

---

## 🌐 **API Endpoints**

### **Public Endpoints**
```
POST   /api/generate-dataset     # Start new dataset generation
GET    /api/job-status/{job_id}  # Check progress
GET    /api/health                # Health check
POST   /api/auth/register         # Register user
POST   /api/auth/login            # Login user
```

### **Protected Endpoints** (require JWT token)
```
GET    /api/auth/me               # Get current user
GET    /api/my-jobs               # Get user's datasets
DELETE /api/jobs/{job_id}         # Cancel/delete job
```

### **Download Endpoints**
```
GET    /api/quality-report/{job_id}     # Get quality report
GET    /api/download/{job_id}/{format}  # Download dataset
       formats: csv, json, excel, parquet, huggingface
```

---

## 🔧 **Configuration Files Explained**

### **backend/config/settings.py**
Loads environment variables:
- API keys (Groq, OpenRouter, Claude, GPT)
- Database URL (PostgreSQL/SQLite)
- Redis URL (Upstash)
- JWT secret
- Storage paths

### **backend/config/languages.py**
Defines for each language:
- Name (e.g., "Hindi", "Gujarati")
- Reddit subreddits to scrape
- YouTube channels to scrape
- Google Play apps to scrape
- News domains to scrape
- Scraper multiplier (boost for low-resource languages)

---

## 🎨 **Supported Features**

### **Languages (8)**
- Hindi (hi)
- Gujarati (gu)
- Tamil (ta)
- Marathi (mr)
- Bengali (bn)
- Telugu (te)
- Kannada (kn)
- English (en)

### **Label Types (3)**
- **Sentiment:** positive / neutral / negative
- **Intent:** question / statement / command / exclamation
- **Toxicity:** toxic / offensive / safe

### **Export Formats (5)**
- CSV (data.csv)
- JSON (data.json)
- Excel (data.xlsx)
- Parquet (data.parquet)
- HuggingFace (dataset folder)

### **Data Sources (4)**
- Reddit posts & comments
- YouTube comments
- Google Play Store reviews
- News articles

---

## 📊 **Dataset Schema (22 Columns)**

Every exported dataset has these columns:

| Column | Description |
|--------|-------------|
| `dataset_id` | Unique dataset identifier |
| `row_id` | Row number |
| `text_original` | Original scraped text |
| `text_clean` | Cleaned text |
| `label_sentiment` | Sentiment label (if selected) |
| `label_intent` | Intent label (if selected) |
| `label_toxicity` | Toxicity label (if selected) |
| `confidence` | AI confidence score (0.0-1.0) |
| `language` | Detected language code |
| `source` | Data source (reddit/youtube/play/news) |
| `source_url` | Original URL |
| `domain` | Content domain (politics/tech/etc) |
| `created_at` | Timestamp |
| `needs_review` | Flagged for human review? |
| `review_reason` | Why flagged (if any) |
| `labels_used` | Which label columns are filled |
| `metadata` | Additional metadata JSON |

Plus 5 more technical columns for processing

---

## 🔐 **Environment Variables Quick Reference**

### **Must Have (Required)**
```env
REDIS_URL=rediss://...upstash.io:6379
DATABASE_URL=postgresql://...supabase.com:6543/postgres
```

### **LLM APIs (At least one required)**
```env
GROQ_API_KEY=gsk_...
OPENROUTER_API_KEY=sk-or-...
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

### **Optional (Have defaults)**
```env
JWT_SECRET_KEY=your-secret-key
FRONTEND_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
DATASETS_STORAGE_PATH=./datasets
```

---

## 🐛 **Common Issues & Fixes**

### **Issue: Backend won't start**
```cmd
# Fix: Install dependencies
cd backend
pip install -r requirements.txt
```

### **Issue: Worker not processing jobs**
```cmd
# Fix: Check Redis connection
# Open .env.local and verify REDIS_URL starts with rediss://
```

### **Issue: "Module not found" error**
```cmd
# Fix: Wrong working directory
# Always run from bhashaData folder, not bhashaData/backend
cd d:\pas\bhashaData
```

### **Issue: Port 8000 already in use**
```cmd
# Fix: Kill existing process
netstat -ano | findstr :8000
taskkill /PID <pid_number> /F
```

### **Issue: Database connection error**
```
# Fix: Check DATABASE_URL format
postgresql://username:password@host:port/database
```

---

## 📈 **Typical Performance**

| Metric | Value |
|--------|-------|
| **Scraping Speed** | 100-500 rows/minute |
| **Cleaning Rate** | 90-95% pass rate |
| **Labeling Speed** | 50-100 rows/minute |
| **Total Time (100 rows)** | 2-5 minutes |
| **Total Time (500 rows)** | 8-15 minutes |
| **Confidence Threshold** | ≥ 0.80 |
| **Label Balance Target** | No label > 60% |

---

## 🎓 **How Labeling Works**

### **Sentiment Example**
```
Input Text: "यह बहुत अच्छा है" (This is very good)

LLM Prompt:
"Classify the sentiment of this Hindi text.
Output ONLY: positive, neutral, or negative"

LLM Response: "positive"

Confidence: 0.92

Final Output:
{
  "text_clean": "यह बहुत अच्छा है",
  "label_sentiment": "positive",
  "confidence": 0.92,
  "language": "hi"
}
```

---

## 🚀 **Deployment Options**

### **Option 1: Local Development (Windows)**
- Backend: localhost:8000
- Worker: Celery local process
- Frontend: localhost:3000
- Database: Supabase (cloud)
- Redis: Upstash (cloud)

### **Option 2: Docker Compose (All Local)**
- Backend: Docker container
- Worker: Docker container
- Frontend: Docker container
- Database: SQLite in volume
- Redis: Docker container

### **Option 3: Production (Cloud)**
- Backend: Railway
- Worker: Railway
- Frontend: Vercel
- Database: Supabase
- Redis: Upstash

---

## 🔗 **Useful URLs**

### **Local Development**
- Backend API: http://localhost:8000
- Backend Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health
- Frontend: http://localhost:3000

### **Production**
- Frontend: https://artha-ai.dev
- Backend: https://artha-ai-backend-production.up.railway.app

### **External Services**
- Supabase Dashboard: https://supabase.com/dashboard
- Upstash Console: https://console.upstash.com
- Railway Dashboard: https://railway.app
- Vercel Dashboard: https://vercel.com

---

## 🧪 **Testing Checklist**

### **Backend Health**
- [ ] Backend starts without errors
- [ ] Health endpoint returns `{"status": "ok"}`
- [ ] Swagger docs load at `/docs`
- [ ] Redis connection confirmed

### **Worker Health**
- [ ] Worker starts without errors
- [ ] Worker shows "ready" status
- [ ] Worker connects to Redis queue
- [ ] Worker can pick up tasks

### **End-to-End Test**
- [ ] Submit dataset generation request
- [ ] Job status updates (scraping → complete)
- [ ] Dataset files generated
- [ ] Quality report available
- [ ] Download works for all formats

---

## 📞 **Getting Help**

1. **Check these files first:**
   - `PROJECT_FLOW.md` (complete flow explanation)
   - `LOCAL_SETUP.md` (setup issues)
   - `info.md` (technical details)

2. **Check logs:**
   - Backend: Look at terminal running uvicorn
   - Worker: Look at terminal running celery
   - Frontend: Look at browser console

3. **Verify environment:**
   - Python version: `python --version` (should be 3.11)
   - Dependencies: `pip list` (check all packages installed)
   - Environment vars: Check `.env.local` file

---

## 🎯 **Quick Tips**

✅ **Always run from project root** (`d:\pas\bhashaData`)  
✅ **Use `.env.local` for development** (not `.env`)  
✅ **Check Redis URL format** (must start with `rediss://`)  
✅ **Use batch scripts** (`start_local.bat`) for easy startup  
✅ **Monitor both windows** (backend + worker) for errors  
✅ **Test health endpoint** before generating datasets  
✅ **Keep API keys secure** (never commit to git)  

---

**Need the full flow?** → Read `PROJECT_FLOW.md`  
**Need setup help?** → Read `LOCAL_SETUP.md`  
**Need technical details?** → Read `info.md`  

**Last Updated:** July 6, 2026
