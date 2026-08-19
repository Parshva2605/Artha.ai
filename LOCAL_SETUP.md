# Artha AI — Local Development Setup (Windows)

## Prerequisites

Install these if not already installed:

1. **Python 3.11** — https://www.python.org/downloads/release/python-3110/
2. **Node.js 18+** — https://nodejs.org/
3. **Git** — https://git-scm.com/

## First Time Setup

### Step 1: Install Python dependencies

Open Command Prompt in `bhashaData/backend` folder:

```cmd
pip install -r requirements.txt
```

### Step 2: Install Node dependencies

Open Command Prompt in `bhashaData/frontend` folder:

```cmd
npm install
```

### Step 3: Set up environment file

Copy `.env.local` and fill in your API keys:

- `GROQ_API_KEY` (from console.groq.com)
- `OPENROUTER_API_KEY` (from openrouter.ai)
- `REDIS_URL` (your Upstash URL — already in production .env)
- `DATABASE_URL` (your Supabase URL — already in production .env)
- `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`

**Note:** The `backend/.env.local` file is already created with production cloud credentials. The `frontend/.env.local` file needs to be created manually (it's gitignored for security).

Create `bhashaData/frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running Locally Every Day

### Option A: Run backend + worker (backend only)

Double-click: `bhashaData/backend/start_local.bat`

This opens 2 windows:
- **Window 1:** FastAPI backend on port 8000
- **Window 2:** Celery worker

Then open browser: http://localhost:8000/api/health

Should return: `{"status": "ok"}`

### Option B: Run everything locally (backend + frontend)

First run `start_local.bat` (backend + worker)

Then in a new terminal:
```cmd
cd bhashaData/frontend
npm run dev
```

Open browser: http://localhost:3000

### Option C: Local backend + Vercel frontend (recommended)

1. Run `start_local.bat` (starts backend + worker locally)
2. Install ngrok: https://ngrok.com/download
3. Open new terminal: `ngrok http 8000`
4. Copy the ngrok URL (like `https://abc123.ngrok.io`)
5. Go to Vercel dashboard → artha-ai.dev → Settings → Environment Variables
6. Set `NEXT_PUBLIC_API_URL` = `https://abc123.ngrok.io`
7. Redeploy Vercel
8. Now artha-ai.dev talks to your local backend!

## Switching Back to Railway

When ready to deploy to Railway again:

1. Go to Vercel → Environment Variables
2. Set `NEXT_PUBLIC_API_URL` back to:
   ```
   https://artha-ai-backend-production.up.railway.app
   ```
3. Redeploy Vercel
4. Push code to GitHub (Railway auto-redeploys)

## Checking Everything Works

- **Backend health:** http://localhost:8000/api/health
- **Backend docs:** http://localhost:8000/docs
- **Frontend:** http://localhost:3000

## Common Windows Errors and Fixes

**Error:** "celery is not recognized"  
**Fix:** `pip install celery`

**Error:** "uvicorn is not recognized"  
**Fix:** `pip install uvicorn`

**Error:** "ModuleNotFoundError: No module named 'backend'"  
**Fix:** Run commands from `bhashaData` folder, not `bhashaData/backend`

**Error:** Redis connection refused  
**Fix:** Check `REDIS_URL` in `.env.local` — must be the Upstash `rediss://` URL

**Error:** Port 8000 already in use  
**Fix:** Run this in CMD: `netstat -ano | findstr :8000`  
Then: `taskkill /PID <pid_number> /F`

**Error:** Database connection failed  
**Fix:** Verify `DATABASE_URL` in `.env.local` is correct Supabase PostgreSQL URL

**Error:** Frontend can't connect to backend  
**Fix:** Check CORS settings in `backend/main.py` and ensure `http://localhost:3000` is in allowed origins

## Architecture Overview

- **Backend:** FastAPI on port 8000
- **Worker:** Celery with Redis broker (Upstash)
- **Database:** PostgreSQL on Supabase
- **Storage:** Supabase Storage
- **Frontend:** Next.js on port 3000 (local) or Vercel (production)

## Environment Files

- `backend/.env.local` — Local development (gitignored, but committed for team use)
- `backend/.env` — Production Railway config (gitignored, contains secrets)
- `frontend/.env.local` — Local frontend config (gitignored, create manually)

## Security Notes

⚠️ **Never commit:**
- API keys to `.env` files
- Database passwords
- JWT secrets for production

✅ **Safe to commit:**
- `.env.example` templates
- `.env.local` IF it only contains localhost URLs and dev-only keys
- Startup scripts (`.bat` and `.ps1` files)
