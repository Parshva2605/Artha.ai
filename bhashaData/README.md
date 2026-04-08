# BhashaData

Dataset generation platform for Indian languages.

## Phase 0 Status

- Frontend scaffolded with Next.js + TypeScript + Tailwind + shadcn base + React Query provider.
- Backend scaffolded with FastAPI + Celery + Redis config + SQLAlchemy SQLite base.
- Docker compose baseline added for frontend, backend, worker, and redis.
- Full folder structure created per project brief.

## Deployment

### Environment Variables Required

#### Backend (Railway)
```env
DATABASE_URL=postgresql://user:password@host:5432/db_name
REDIS_URL=rediss://your-upstash-url
JWT_SECRET_KEY=your-secret-key-min-32-chars-change-in-production
FRONTEND_URL=https://your-frontend.vercel.app
ANTHROPIC_API_KEY=sk-...
OPENAI_API_KEY=sk-...
OLLAMA_BASE_URL=https://api.ollama.com
OLLAMA_API_KEY=...
OLLAMA_MODEL=qwen3-next:80b-cloud
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=ArthAI/1.0
DATASETS_STORAGE_PATH=/tmp/datasets
```

#### Frontend (Vercel)
```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

### Deployment Steps

#### Backend on Railway
1. Push code to GitHub repository
2. Connect GitHub repo to Railway
3. Add service PostgreSQL (Supabase recommended)
4. Add plugin Redis (Upstash recommended)
5. Set environment variables from section above
6. Deploy

#### Frontend on Vercel
1. Push code to GitHub repository
2. Connect frontend folder to Vercel
3. Set `NEXT_PUBLIC_API_URL` environment variable
4. Deploy

### Database Migrations

For Supabase PostgreSQL, tables are created automatically on first run via SQLAlchemy `Base.metadata.create_all()`.

### Authentication

- **JWT tokens** stored in localStorage
- **Bearer token** required for authenticated endpoints
- **Token expiry**: 7 days (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Password hashing**: bcrypt via passlib

### API Endpoints

**Public:**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/generate-dataset` - Generate dataset (optional auth)
- `GET /api/job-status/{job_id}` - Check job status
- `GET /api/health` - Health check

**Protected (requires authentication):**
- `GET /api/auth/me` - Get current user
- `GET /api/my-jobs` - Get user's datasets
- `POST /api/auth/logout` - Logout (frontend handles)

