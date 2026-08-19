# 📊 Artha AI / BhashaData - Complete Project Flow

## 🎯 **What This Project Does**

**Artha AI** is a multilingual dataset generation platform for **Indian languages** (Hindi, Gujarati, Tamil, Marathi, etc.). It scrapes text from multiple sources, cleans it, labels it with AI, and exports ready-to-use datasets for training AI models.

---

## 🏗️ **Architecture Overview**

```
┌─────────────────┐
│   User Browser  │
│  (Frontend UI)  │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  FastAPI Backend│◄──────┐
│   Port 8000     │       │
└────────┬────────┘       │
         │                │
         │ Creates Job    │ Reads Status
         │                │
         ▼                │
┌─────────────────┐       │
│  PostgreSQL DB  │       │
│  (Job Storage)  │       │
└─────────────────┘       │
         │                │
         │ Enqueues Task  │
         │                │
         ▼                │
┌─────────────────┐       │
│  Redis (Queue)  │       │
│    Upstash      │       │
└────────┬────────┘       │
         │                │
         │ Task Pickup    │
         │                │
         ▼                │
┌─────────────────┐       │
│ Celery Worker   │       │
│  (Background)   │───────┘
└────────┬────────┘
         │
         │ Writes Progress
         │
         ▼
┌─────────────────┐
│ Redis (Status)  │
│  Live Progress  │
└─────────────────┘
         │
         │ Generates Files
         │
         ▼
┌─────────────────┐
│ Datasets Folder │
│  CSV/JSON/etc   │
└─────────────────┘
```

---

## 🔄 **Complete Flow: User Request to Dataset Download**

### **Step 1: User Submits Request (Frontend)**

**File:** `frontend/app/generate/page.tsx`

User fills form:
- Languages: Hindi, Gujarati, Tamil, Marathi
- Quantity: 100 rows per language
- Label Type: Sentiment, Intent, or Toxicity
- Export Formats: CSV, JSON, Excel, Parquet, HuggingFace
- Domain: Politics, Technology, Entertainment, etc.

**Frontend sends POST request:**
```javascript
POST /api/generate-dataset
{
  "languages": ["hi", "gu"],
  "quantity_per_language": 100,
  "label_type": "sentiment",
  "export_formats": ["csv", "json"],
  "domain": "general"
}
```

---

### **Step 2: Backend Creates Job (FastAPI)**

**File:** `backend/api/routes.py`

```python
@router.post("/generate-dataset")
async def generate_dataset(request):
    # 1. Generate unique job_id
    job_id = str(uuid4())
    
    # 2. Save job to database
    create_job(db, job_id, request, email, user_id)
    
    # 3. Send task to Celery queue
    generate_dataset_task.apply_async(
        args=[job_id, request],
        task_id=job_id
    )
    
    # 4. Return job_id to frontend
    return {"job_id": job_id}
```

**What happens:**
- Job record created in PostgreSQL with status = "queued"
- Task added to Redis queue (Celery broker)
- Frontend receives job_id

---

### **Step 3: Celery Worker Picks Up Task**

**File:** `backend/workers/dataset_job.py`

```python
@celery_app.task
def generate_dataset_task(job_id, request_payload):
    # STAGE 1: SCRAPING
    update_status(job_id, "scraping", 15%)
    raw_data = scrape_all_sources(languages)
    
    # STAGE 2: CLEANING
    update_status(job_id, "cleaning", 35%)
    clean_data = clean_pipeline(raw_data)
    
    # STAGE 3: LABELING
    update_status(job_id, "labeling", 60%)
    labeled_data = label_with_llm(clean_data)
    
    # STAGE 4: QUALITY CHECK
    update_status(job_id, "quality_check", 80%)
    quality_report = check_quality(labeled_data)
    
    # STAGE 5: EXPORT
    update_status(job_id, "exporting", 92%)
    export_files(labeled_data, formats)
    
    # STAGE 6: COMPLETE
    update_status(job_id, "complete", 100%)
```

---

## 🔍 **Detailed Stage Breakdown**

### **STAGE 1: SCRAPING (15% Progress)**

**File:** `backend/scrapers/orchestrator.py`

**What it does:**
- Runs 4 scrapers in parallel for each language:
  1. **Reddit** (`reddit.py`) - r/india, r/gujarati, etc.
  2. **YouTube** (`youtube.py`) - Comments from Indic channels
  3. **Google Play** (`google_play.py`) - App reviews
  4. **News** (`news.py`) - News articles

**Example for Hindi:**
```python
# Reddit: Scrape r/india, r/hindi
reddit_data = scrape_reddit(subreddits=["india", "hindi"], limit=25)

# YouTube: Scrape comments
youtube_data = scrape_youtube_comments(video_urls=[...], limit=50)

# Google Play: Scrape app reviews
play_data = scrape_google_play(app_ids=["com.whatsapp"], limit=25)

# News: Scrape articles
news_data = scrape_news(urls=["timesofindia.com"], limit=25)

# Combine all
raw_data = reddit_data + youtube_data + play_data + news_data
```

**Output:** Raw text rows with source metadata

---

### **STAGE 2: CLEANING (35% Progress)**

**File:** `backend/pipeline/cleaner.py`

**What it does:**
1. **Language Detection** - Verify text is in correct language
2. **Deduplication** - Remove exact duplicates
3. **Noise Removal** - Remove URLs, emails, excessive punctuation
4. **Length Filter** - Remove text < 10 chars or > 500 chars
5. **Script Validation** - Verify Devanagari/Gujarati/Tamil scripts

**Example:**
```python
# Before cleaning
raw_text = "Check out this link: https://example.com !!! 🔥🔥🔥"

# After cleaning
clean_text = "Check out this link"
```

**Output:** Clean text rows, language-verified

---

### **STAGE 3: LABELING (60% Progress)**

**File:** `backend/pipeline/labeler.py`

**What it does:**
- Uses LLM (Groq, OpenRouter, Claude, GPT) to label each text
- Supports 3 label types:

**1. Sentiment:**
```
positive / neutral / negative
```

**2. Intent:**
```
question / statement / command / exclamation
```

**3. Toxicity:**
```
toxic / offensive / safe
```

**Example API call to LLM:**
```python
prompt = f"""
Language: Hindi
Text: {text}
Task: Classify sentiment as positive, neutral, or negative.
Output ONLY: positive/neutral/negative
"""

response = llm_client.generate(prompt)
label = parse_label(response)  # "positive"
confidence = 0.92
```

**Output:** Labeled rows with confidence scores

---

### **STAGE 4: QUALITY CHECK (80% Progress)**

**File:** `backend/pipeline/quality.py`

**What it checks:**
1. **Confidence threshold** - All rows > 0.80 confidence
2. **Label balance** - No label > 60% of data
3. **Language distribution** - Each language meets minimum 80%
4. **Overall quality score** - Weighted average

**Example quality report:**
```json
{
  "overall_quality_score": 0.89,
  "per_language_quality": {
    "hi": 0.91,
    "gu": 0.87
  },
  "label_distribution": {
    "positive": 35,
    "neutral": 40,
    "negative": 25
  },
  "warnings": [
    "Gujarati delivered 75 rows (requested 100, minimum 80)"
  ]
}
```

---

### **STAGE 5: EXPORT (92% Progress)**

**File:** `backend/pipeline/exporter.py`

**What it exports:**

**1. CSV File** (`data.csv`)
```csv
text_clean,label_sentiment,confidence,language,source
"यह बहुत अच्छा है",positive,0.92,hi,reddit
"આ સરસ છે",positive,0.89,gu,youtube
```

**2. JSON File** (`data.json`)
```json
[
  {
    "text_clean": "यह बहुत अच्छा है",
    "label_sentiment": "positive",
    "confidence": 0.92,
    "language": "hi",
    "source": "reddit"
  }
]
```

**3. Excel File** (`data.xlsx`)
- Same as CSV but in .xlsx format

**4. Parquet File** (`data.parquet`)
- Columnar format for big data processing

**5. HuggingFace Dataset**
- Folder with `dataset_info.json` + `data.parquet`
- Ready to push to HuggingFace Hub

**6. Metadata File** (`metadata.json`)
```json
{
  "dataset_id": "abc123",
  "created_at": "2026-07-06T...",
  "languages": ["hi", "gu"],
  "total_rows": 175,
  "quality_score": 0.89,
  "label_distribution": {...},
  "warnings": [...]
}
```

**Output location:** `datasets/<job_id>/`

---

### **STAGE 6: COMPLETE (100% Progress)**

**What happens:**
1. Job status updated to "complete" in PostgreSQL
2. Redis status cache updated
3. Frontend shows "Download Ready"

---

## 🖥️ **Frontend Flow**

### **Page 1: Generate Dataset**
**File:** `frontend/app/generate/page.tsx`

User selects options → Submits → Gets `job_id`

---

### **Page 2: Progress Tracking**
**File:** `frontend/app/job/[id]/page.tsx`

Polls backend every 2 seconds:
```javascript
GET /api/job-status/{job_id}
```

Response:
```json
{
  "job_id": "abc123",
  "status": "labeling",
  "progress_percent": 60,
  "current_step": "Labeling",
  "per_language_status": {
    "hi": {
      "rows_collected": 100,
      "rows_clean": 95,
      "rows_labeled": 90
    }
  },
  "eta_seconds": 120
}
```

Shows progress bar, language-wise status, ETA

---

### **Page 3: Download & Quality Report**
**File:** `frontend/app/download/[id]/page.tsx`

Shows:
- Overall quality score
- Per-language breakdown
- Label distribution chart
- Warnings (if any)
- Download buttons (CSV, JSON, Excel, etc.)

---

## 🗄️ **Database Schema**

### **Jobs Table**
```sql
CREATE TABLE jobs (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(36),
    status VARCHAR(32),         -- queued/scraping/cleaning/labeling/complete
    request_payload TEXT,       -- Original request JSON
    result_summary TEXT,        -- Quality report JSON
    output_dir VARCHAR(255),    -- datasets/<job_id>
    exported_formats TEXT,      -- ["csv", "json"]
    error_message TEXT,
    created_at DATETIME,
    updated_at DATETIME
)
```

### **Users Table** (for authentication)
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    hashed_password VARCHAR(255),
    full_name VARCHAR(255),
    is_active BOOLEAN,
    created_at DATETIME
)
```

---

## 🔧 **Configuration Files**

### **Language Configuration**
**File:** `backend/config/languages.py`

```python
LANGUAGE_CONFIGS = {
    "hi": {  # Hindi
        "name": "Hindi",
        "reddit_subreddits": ["india", "hindi", "bollywood"],
        "youtube_channels": ["NDTV", "AajTak"],
        "google_play_apps": ["com.whatsapp", "com.facebook"],
        "news_domains": ["timesofindia.com", "ndtv.com"],
        "effective_scraper_multiplier": 1.0,
        "example_prefix": "नमस्ते"
    },
    "gu": {  # Gujarati
        "name": "Gujarati",
        "reddit_subreddits": ["gujarat", "ahmedabad"],
        "youtube_channels": ["TV9Gujarati"],
        "google_play_apps": ["com.whatsapp"],
        "news_domains": ["sandesh.com", "divyabhaskar.com"],
        "effective_scraper_multiplier": 5.0,  # 5x boost for Gujarati
        "example_prefix": "નમસ્તે"
    }
}
```

---

## 🔑 **Environment Variables**

### **Backend (.env.local)**
```env
# LLM APIs
GROQ_API_KEY=gsk_...
OPENROUTER_API_KEY=sk-or-...

# Cloud Services
REDIS_URL=rediss://...upstash.io:6379        # Upstash Redis
DATABASE_URL=postgresql://...supabase.com... # Supabase PostgreSQL

# Authentication
JWT_SECRET_KEY=your-secret-key-32-chars

# URLs
NEXT_PUBLIC_API_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# Storage
DATASETS_STORAGE_PATH=./datasets
```

---

## 🎨 **Tech Stack Summary**

| Component | Technology |
|-----------|-----------|
| **Frontend** | Next.js 14 + React 18 + TypeScript + TailwindCSS |
| **Backend API** | FastAPI 0.115 + Python 3.11 |
| **Task Queue** | Celery 5.4 + Redis 5.0 |
| **Database** | PostgreSQL (Supabase) / SQLite (local) |
| **LLM APIs** | Groq, OpenRouter, Claude, GPT |
| **Scrapers** | PRAW (Reddit), yt-dlp (YouTube), google-play-scraper |
| **Data Processing** | pandas, langdetect, beautifulsoup4 |
| **Export Formats** | CSV, JSON, Excel, Parquet, HuggingFace |
| **Deployment** | Railway (backend), Vercel (frontend) |

---

## 📈 **Performance Characteristics**

- **Scraping:** 100-500 rows per language in 30-60 seconds
- **Cleaning:** 90-95% of raw data passes filters
- **Labeling:** 50-100 rows per minute (depends on LLM API)
- **Total Time:** 2-10 minutes for 100 rows per language
- **Quality:** >0.80 confidence on all labels
- **Balance:** No label exceeds 60% of dataset

---

## ⚠️ **Known Limitations**

1. **Yield Variance:** Some languages (Gujarati) have fewer online sources
2. **API Dependency:** Requires LLM API keys (Groq/OpenRouter)
3. **Rate Limits:** Reddit/YouTube APIs have rate limits
4. **Language Detection:** Not 100% accurate for code-mixed text
5. **Label Quality:** Depends on LLM prompt engineering

---

## 🚀 **How to Use This Project**

### **Option 1: Run Everything Locally**
```cmd
cd d:\pas\bhashaData\backend
start_local.bat
```

### **Option 2: Docker Compose**
```cmd
cd d:\pas\bhashaData
docker compose up --build
```

### **Option 3: Production (Railway + Vercel)**
- Backend on Railway
- Frontend on Vercel
- Database on Supabase
- Redis on Upstash

---

## 📚 **Key Files to Understand**

**Must Read (Priority Order):**
1. `docker-compose.yml` - Infrastructure
2. `backend/workers/dataset_job.py` - Core pipeline
3. `backend/scrapers/orchestrator.py` - Scraping logic
4. `backend/pipeline/cleaner.py` - Cleaning logic
5. `backend/pipeline/labeler.py` - Labeling logic
6. `backend/pipeline/quality.py` - Quality checks
7. `backend/config/languages.py` - Language configs
8. `frontend/app/generate/page.tsx` - UI entry point
9. `frontend/app/job/[id]/page.tsx` - Progress UI
10. `frontend/app/download/[id]/page.tsx` - Download UI

---

## 🎓 **Example Use Cases**

1. **Train sentiment model for Hindi e-commerce reviews**
   - Scrape: Product reviews
   - Label: Positive/Neutral/Negative
   - Use: Fine-tune BERT model

2. **Build Gujarati chatbot intent classifier**
   - Scrape: Social media conversations
   - Label: Question/Statement/Command
   - Use: Train intent detection model

3. **Create toxicity filter for Tamil content**
   - Scrape: Comments, forums
   - Label: Toxic/Offensive/Safe
   - Use: Content moderation system

---

## 🔮 **Future Improvements**

1. Add more languages (Bengali, Telugu, Kannada)
2. Add custom label types (emotion, urgency, etc.)
3. Add data augmentation (paraphrasing, translation)
4. Add active learning (human review loop)
5. Add dataset versioning
6. Add collaborative features (team workspaces)
7. Add payment integration (Razorpay)
8. Add API rate limiting and quotas

---

**Last Updated:** July 6, 2026  
**Version:** 2.2  
**Status:** Production Ready
