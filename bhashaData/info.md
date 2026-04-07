# BhashaData / Artha AI - Full Project Handoff

## 1) Project Summary
BhashaData is a multilingual dataset generation platform focused on Indian languages. It provides a web UI + API + background worker pipeline to:
- Collect text from multiple public sources.
- Clean and language-filter the collected text.
- Label text with LLM-assisted annotations.
- Score quality and detect shortfalls.
- Export final datasets in multiple formats.

Primary use cases:
- Topic/sentiment model training in Indic languages.
- Social/news/app feedback analytics.
- Academic dataset and pipeline benchmarking.

## 2) Tech Stack
Frontend:
- Next.js 14.2.5
- React 18.3.1
- TypeScript
- TailwindCSS
- TanStack React Query

Backend:
- FastAPI 0.115.0
- Celery 5.4.0
- Redis 5.0.8
- SQLAlchemy 2.0.34
- Pydantic v2

Data/Scraping/ML libs:
- praw
- youtube-comment-downloader
- yt-dlp
- google-play-scraper
- requests + beautifulsoup4
- langdetect
- anthropic + openai clients
- pandas + pyarrow + openpyxl + datasets

Deployment:
- Docker Compose with services: redis, backend, worker, frontend

## 3) High-Level Architecture
Flow:
1. User submits generation request from frontend.
2. Backend creates job row in DB and enqueues Celery task.
3. Worker runs scrape -> clean -> label -> quality -> export.
4. Worker writes live progress/status to Redis.
5. Frontend polls job status endpoint and updates progress UI.
6. On completion, frontend downloads files and shows quality report.

Core runtime state:
- Persistent job metadata: SQLite.
- Real-time progress cache: Redis.
- Artifacts: datasets folder.

## 4) Current Folder Structure
Project root: d:/pas/bhashaData

Top-level:
- backend/
- frontend/
- datasets/
- docker-compose.yml
- .env
- .env.example
- README.md
- info.md

Backend major folders:
- backend/api
- backend/config
- backend/database
- backend/pipeline
- backend/scrapers
- backend/workers
- backend/tests

Frontend major folders:
- frontend/app
- frontend/components
- frontend/lib
- frontend/types

## 5) Important Files and Purpose
Backend:
- backend/main.py: FastAPI app bootstrap.
- backend/api/routes.py: API endpoints (generate, status, health, quality, download).
- backend/api/models.py: request/response schemas.
- backend/database/db.py: DB engine/session.
- backend/database/models.py: Job/DatasetArtifact models and CRUD helpers.
- backend/config/settings.py: env-driven runtime settings.
- backend/config/languages.py: supported language configs and source lists.
- backend/workers/celery_app.py: Celery app config and task routing.
- backend/workers/dataset_job.py: full pipeline task execution + progress updates.
- backend/workers/status.py: Redis status read/write helpers.
- backend/scrapers/orchestrator.py: runs all scrapers per language.
- backend/scrapers/reddit.py, youtube.py, google_play.py, news.py: source adapters.
- backend/pipeline/cleaner.py: cleaning, language checks, dedup.
- backend/pipeline/labeler.py: LLM labeling logic.
- backend/pipeline/quality.py: quality scoring, balance checks, shortfall warnings.
- backend/pipeline/exporter.py: CSV/JSON/Excel/Parquet/HuggingFace export + metadata.
- backend/tests/*.py: unit + integration coverage.
- backend/INTEGRATION_TEST_REPORT.md: prior integration pass summary.

Frontend:
- frontend/app/page.tsx: landing page.
- frontend/app/generate/page.tsx: multi-step generation form.
- frontend/app/job/[id]/page.tsx: progress polling page.
- frontend/app/download/[id]/page.tsx: quality + download page.
- frontend/app/docs/page.tsx: docs page.
- frontend/lib/api.ts: frontend API client.
- frontend/lib/types.ts: shared frontend domain types.
- frontend/components/*: selectors, progress tracker, quality/report cards.

Infra:
- docker-compose.yml: all services and runtime env wiring.
- backend/Dockerfile and frontend/Dockerfile: image definitions.

## 6) API Endpoints (Operational)
- POST /api/generate-dataset
- GET /api/job-status/{job_id}
- GET /api/quality-report/{job_id}
- GET /api/download/{job_id}/{format}
- GET /api/health

## 7) Requested Feature/Phase Timeline (What Was Done)
Initial scaffold phase:
- Frontend and backend base project created.
- Compose stack and basic DB/worker plumbing created.

Frontend implementation/audit phase:
- Full generation UX completed.
- Job and download pages implemented.
- Validation and accessibility fixes applied.
- Build/type checks completed.

Integration phase:
- Real end-to-end pipeline tests added.
- Integration report generated with pass status.

Docker stabilization phase:
- Fixed backend package import path in containers.
- Fixed worker and backend command/module paths.
- Fixed Redis URL mismatch in containers.
- Fixed worker queue subscription mismatch.
- Fixed backend/worker DB split by using shared DB path in compose.

Multilingual quality improvement phase:
- Improved Indic script-aware language acceptance in cleaner.
- Expanded news URL extraction behavior for non-English sources.
- Increased Reddit fetch breadth and relaxed non-English news gate.
- Reduced news per-article delay to improve throughput.
- Added per-language row counters in progress updates.

Gujarati-focused enhancement phase:
- Added Gujarati source expansions in language config.
- Added Gujarati-specific effective scraper multiplier (5x).
- Added stricter shortfall warning details in quality report.
- Added minimum acceptable warning messages for per-language delivery.
- Improved fallback generation scale to avoid tiny low-yield outputs in sparse-source scenarios.

## 8) Key Bugs Found and Resolved
1. Jobs stuck at queued/0%:
- Cause: task routed to dataset_generation queue while worker listened only to celery.
- Fix: worker now listens to dataset_generation,celery and Celery default queue alignment added.

2. Worker error Job not found:
- Cause: backend and worker used separate relative SQLite files.
- Fix: both services now use DATABASE_URL=sqlite:////datasets/bhashaData.db with shared volume.

3. Non-English under-collection:
- Cause: strict filters + low source hit rate + narrow URL heuristics.
- Fix: Indic script-aware checks, broader source coverage, increased Gujarati targeting.

4. Misleading UI row counters:
- Cause: per-language counters not updated through stages.
- Fix: rows_collected/rows_clean/rows_labeled now update per stage completion.

## 9) Current Docker Runtime Configuration (Important)
In docker-compose.yml:
- Backend and worker use:
  - REDIS_URL=redis://redis:6379
  - DATABASE_URL=sqlite:////datasets/bhashaData.db
  - DATASETS_STORAGE_PATH=/datasets
- Worker command listens to dataset queue:
  - celery ... -Q dataset_generation,celery

## 10) Quality Logic (Current)
Quality report computes:
- Overall confidence score.
- Per-language quality.
- Label distribution and balance.
- English benchmark comparison note.
- Shortfall warnings.
- Low quality warning under threshold.

Minimum rows warning behavior:
- For each requested language:
  - delivered < 80% of requested triggers explicit warning message.
  - warning includes language name, delivered rows, requested rows, minimum acceptable rows, and advice to increase scrape target_count.

## 11) Final Gujarati Verification (Latest)
Verification script run:
- get_config_by_code("gu")
- run_scrapers_for_language(... target_count=100)
- run_cleaning_pipeline(...)
- assert clean.total_output >= 80

Observed output:
- Gujarati scraped: 800
- Gujarati clean: 800
- GUJARATI FIX VERIFIED

## 12) Dataset Quality Review (Audited File)
Audited file:
- C:/Users/91851/Downloads/data (1).csv

Measured stats:
- Total rows: 263
- Duplicate full rows: 0
- Duplicate text_clean rows: 0
- Language distribution:
  - ta: 75 (28.52%)
  - mr: 75 (28.52%)
  - hi: 70 (26.62%)
  - gu: 43 (16.35%)
- Topic distribution skew exists (technology/politics/other dominant).
- Confidence avg: 0.9148, min: 0.8, max: 1.0.
- Low confidence (<0.7): 0.
- Needs review true: 0.
- Short text < 4 words: 0.
- Script mismatch estimate: 0.

Interpretation:
- Data is clean and usable for prototyping/academic work.
- Main risk is multilingual balance, especially Gujarati underrepresentation in that older artifact.
- Recent Gujarati pipeline changes were introduced to improve this.

## 13) Generated Artifacts Format
Typical output per job under datasets/<job_id>/:
- data.csv
- data.json
- data.xlsx (if requested)
- data.parquet (if requested)
- huggingface/ (if requested)
- metadata.json

metadata.json includes:
- dataset_id/job_id
- created_at
- languages
- label_types
- domain
- total_rows
- per_language requested vs delivered
- quality scores
- label distributions
- source list
- export formats
- llm usage counts
- benchmark note
- shortfall warnings

## 14) How to Run (Team Quickstart)
Prerequisites:
- Docker Desktop running.

Commands:
1. cd d:/pas/bhashaData
2. docker compose up --build
3. Frontend: http://localhost:3000
4. Backend health: http://localhost:8000/api/health

Local Python quick run pattern:
- d:/pas/.venv-1/Scripts/python.exe <script_or_-c>

## 15) Testing and Validation Notes
Backend tests exist in backend/tests.
Integration test file:
- backend/tests/test_e2e_generation.py

Known practical note:
- Live scraping quality and yield depend on external source availability and API access at run time.

## 16) Current Strengths and Risks
Strengths:
- End-to-end async architecture is functional.
- Dockerized local deployment works.
- Progress and quality reporting are integrated.
- Exports support multiple ML-friendly formats.

Risks / open improvements:
- Yield variance across languages can still occur under real internet/API conditions.
- Class balance can be skewed by source mix.
- Strong fallback can improve pass rates but may reduce data diversity if overused.

## 17) Recommended Next Steps
1. Add hard blocking gate (not only warning) when delivered rows per language < threshold.
2. Add source-level quotas to prevent one source dominating.
3. Add periodic language/source diagnostics to metadata.
4. Add retry/backoff strategy per scraper and per language.
5. Add CI checks for minimum language distribution and class balance.

## 18) Handoff Note for Other AI / Team Members
When analyzing this project, prioritize these files first:
1. docker-compose.yml
2. backend/workers/dataset_job.py
3. backend/scrapers/orchestrator.py
4. backend/pipeline/cleaner.py
5. backend/pipeline/quality.py
6. backend/config/languages.py
7. backend/pipeline/exporter.py
8. frontend/app/generate/page.tsx
9. frontend/app/job/[id]/page.tsx
10. frontend/app/download/[id]/page.tsx

These files contain the core behavior, recent fixes, and quality logic.
