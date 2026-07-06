@echo off
echo Starting Artha AI Local Development
echo =====================================
echo Step 1: Loading local environment...
for /f "tokens=1,2 delims==" %%a in (.env.local) do (
    if not "%%a"=="" if not "%%b"=="" set "%%a=%%b"
)

echo Step 2: Starting FastAPI backend...
start "Artha Backend" cmd /k "cd /d %~dp0 && uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

echo Step 3: Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak > nul

echo Step 4: Starting Celery worker...
start "Artha Worker" cmd /k "cd /d %~dp0 && celery -A backend.workers.celery_app.celery_app worker -l info --pool=solo -Q dataset_generation,celery"

echo =====================================
echo Backend running at: http://localhost:8000
echo Health check: http://localhost:8000/api/health
echo =====================================
echo Both services started in separate windows.
echo Close those windows to stop the services.
pause
