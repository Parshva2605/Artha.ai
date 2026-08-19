![Status](https://img.shields.io/badge/Status-Live-brightgreen)
![Quality](https://img.shields.io/badge/Quality-98.8%25-brightgreen)
![Languages](https://img.shields.io/badge/Languages-5_Indian-orange)
![License](https://img.shields.io/badge/License-MIT-blue)

# Artha AI

### "Give Meaning to Your Data"

**India's First On-Demand Indian Language Dataset Generation Platform**

[🚀 Try Free](https://artha-ai.dev) | [📖 API Docs](https://artha-ai.dev/docs) | [📧 Contact](mailto:arthaai.dev@gmail.com)

---

## 🔧 Service Status

> **Note:** The backend API is currently paused due to infrastructure maintenance. The platform will be fully restored shortly.
>
> **Frontend:** ✅ Live at artha-ai.dev  
> **Backend API:** ⏸️ Temporarily paused  
> **Database:** ✅ All data safe on Supabase  
>
> For dataset requests during this period, contact: arthaai.dev@gmail.com  
> We will process your request manually.

---

## What is Artha AI?

Artha AI automatically generates labeled AI training datasets in Indian languages. Select your language, domain, and label type. Get a production-ready labeled dataset in 20 minutes at ₹499 per 1000 rows.

No manual labeling. No data collection hassles. Just upload a request and download your dataset.

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Average Quality Score | 98.8% |
| Confidence Threshold | 0.80 minimum |
| Oversample Factor | 4x |
| Delivery Time | ~20 minutes |
| Languages Supported | 5 Indian languages |
| Export Formats | 5 formats |
| Label Types | 4 + custom |

---

## Features

🌐 **5 Indian Languages**  
Hindi, Gujarati, Marathi, Tamil, English

🏷️ **4 Label Types**  
Sentiment, Topic, NER, Custom labels

📤 **5 Export Formats**  
CSV, JSON, Excel, Parquet, HuggingFace

⚡ **Automated Pipeline**  
Scrape → Clean → Label → Balance → Export

🎯 **Custom Labels**  
Define your own categories — complaint, refund, delivery, urgent — any labels

📁 **Upload Own CSV**  
Bring your existing data, we label it

✅ **Quality Guarantee**  
98.8% average confidence score

🔐 **User Accounts**  
Job history, re-download anytime

📱 **Mobile Responsive**  
Works on all devices

---

## How It Works

1️⃣ Select language, domain, label type, quantity  
↓  
2️⃣ AI scrapes YouTube, Google Play, News  
↓  
3️⃣ Cleans and filters by language  
↓  
4️⃣ Groq LLM labels every row  
↓  
5️⃣ Balance enforced — exact row count delivered  
↓  
6️⃣ Quality checked — 98.8% average score  
↓  
7️⃣ Download CSV, JSON, Excel, Parquet, HuggingFace

---

## Supported Languages

| Language | Script | Status |
|----------|--------|--------|
| Hindi | Devanagari | ✅ Live |
| Gujarati | Gujarati | ✅ Live |
| Marathi | Devanagari | ✅ Live |
| Tamil | Tamil | ✅ Live |
| English | Latin | ✅ Live (benchmark) |

---

## Label Types

| Label Type | Categories | Use Case |
|------------|------------|----------|
| Sentiment | positive, negative, neutral | Product reviews, feedback |
| Topic | politics, sports, tech, health, finance, education, entertainment, food, other | News classification |
| NER | PERSON, ORG, LOCATION, DATE, CURRENCY, OTHER | Entity extraction |
| Custom | You define any labels | Any industry specific use |

---

## API Reference

**Base URL:** `https://artha-ai-backend-production.up.railway.app`

### Generate Dataset

```http
POST /api/generate-dataset
```

**Request body:**
```json
{
  "languages": ["hi", "gu"],
  "domain": "ecommerce",
  "label_type": "sentiment",
  "quantity_per_language": 1000,
  "export_formats": ["csv", "json"],
  "custom_labels": null
}
```

**Response:**
```json
{
  "job_id": "uuid",
  "estimated_minutes": 20,
  "message": "Dataset generation queued"
}
```

### Check Job Status

```http
GET /api/job-status/{job_id}
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "labeling",
  "progress_percent": 65,
  "current_step": "Labeled 650/1000 rows"
}
```

### Download Dataset

```http
GET /api/download/{job_id}/{format}
```

Returns: Redirect to Supabase Storage URL

### Upload and Label CSV

```http
POST /api/upload-csv
```

Body: `multipart/form-data` with CSV file  
Returns: `upload_id`, detected columns, preview

```http
POST /api/label-uploaded-csv
```

Body: `upload_id`, `text_column`, `label_type`  
Returns: `job_id` for tracking

### Health Check

```http
GET /api/health
```

Returns: `{ "status": "ok" }`

---

## Tech Stack

### Frontend
- Next.js 14
- TypeScript
- TailwindCSS
- shadcn/ui
- TanStack React Query
- Deployed on Vercel

### Backend
- Python 3.11
- FastAPI
- Celery + Redis
- SQLAlchemy + PostgreSQL
- Supabase Storage
- Deployed on Railway

### AI and Data
- Groq LLM (llama-3.1-8b-instant)
- OpenRouter (fallback)
- langdetect
- pandas, pyarrow
- yt-dlp, google-play-scraper

### Infrastructure
- Supabase (Database + Storage)
- Upstash Redis
- Railway (Backend + Worker)
- Vercel (Frontend)

---

## Architecture

```
┌─────────────────────────────────────┐
│          artha-ai.dev               │
│         (Next.js on Vercel)         │
└──────────────┬──────────────────────┘
               │ REST API
               ▼
┌─────────────────────────────────────┐
│      FastAPI Backend                │
│      (Railway)                      │
└──────┬───────────────┬──────────────┘
       │               │
       ▼               ▼
┌──────────────┐ ┌─────────────────┐
│ Supabase DB  │ │  Redis Queue    │
│ (PostgreSQL) │ │  (Upstash)      │
└──────────────┘ └────────┬────────┘
                          │
                          ▼
                ┌─────────────────────┐
                │   Celery Worker     │
                │   (Railway)         │
                │                     │
                │ Scrape→Clean→Label  │
                │ Balance→Quality     │
                │ Export→Upload       │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │  Supabase Storage   │
                │  datasets/{job_id}/ │
                │  data.csv           │
                │  data.json          │
                │  data.xlsx          │
                └─────────────────────┘
```

---

## Pricing

| Plan | Price | Delivery | Details |
|------|-------|----------|---------|
| Free | ₹0 | 20 min | 100 rows, one time per account |
| Automated | ₹499/1000 rows | ~20 min | Scrapable domains |
| Custom | ₹999/1000 rows | 2-5 days | Medical, legal, agriculture |
| Pro | ₹1,999/month | ~20 min | Unlimited automated |
| Enterprise | Custom quote | Custom | Large scale + SLA |

Volume discounts available for 5000+ rows.

---

## Use Cases

### 🤖 Train a Hindi sentiment classifier
→ Generate 5000 Hindi product review rows  
→ Labeled positive/negative/neutral  
→ Download as HuggingFace dataset  
→ Train your model directly

### 🏷️ Label your customer support tickets
→ Upload CSV with ticket text column  
→ Define labels: complaint, refund, escalation, resolved  
→ Download fully labeled CSV  
→ Automate your support routing

### 📊 Build a Gujarati topic classifier
→ Generate 2000 Gujarati news rows  
→ Labeled across 9 topic categories  
→ Export as CSV or JSON  
→ Ready for fine-tuning

---

## Quality System

Every dataset goes through 6 quality gates:

1. **Language Detection** — only correct language rows pass
2. **Noise Filtering** — URLs, spam, very short text removed
3. **Deduplication** — exact duplicates removed
4. **Confidence Threshold** — rows below 0.80 confidence rejected
5. **Balance Enforcement** — no label exceeds 50% of dataset
6. **Oversample** — 4x rows labeled to deliver only the best

**Result:** 98.8% average confidence score

---

## Roadmap

- ✅ 5 Indian languages
- ✅ Sentiment, Topic, NER labeling
- ✅ Custom label support
- ✅ Upload own CSV for labeling
- ✅ 5 export formats
- ✅ User authentication
- ⬜ Synthetic data generation
- ⬜ 10 more Indian languages
- ⬜ Audio dataset support
- ⬜ Image dataset support
- ⬜ API key based access
- ⬜ Webhook notifications

---

## Contact and Links

🌐 **Website:** https://artha-ai.dev  
📧 **Email:** arthaai.dev@gmail.com  
👨‍💻 **GitHub:** github.com/Parshva2605/Artha.ai  
🐦 **Founded by:** Parshva Shah, Anand, Gujarat

For enterprise inquiries or custom dataset requests contact arthaai.dev@gmail.com

---

## Footer

**Built in Gujarat, India**

© 2025 Artha AI. All rights reserved.

Applied to: iCreate Spark-up Fund | MeitY Startup Hub

**"Give Meaning to Your Data"**
