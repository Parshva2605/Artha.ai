Write-Host "Starting Artha AI Local Development" -ForegroundColor Green

# Load .env.local
Get-Content .env.local | ForEach-Object {
    if ($_ -match '^([^#][^=]*)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), 'Process')
    }
}

Write-Host "Starting FastAPI backend on port 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

Start-Sleep -Seconds 3

Write-Host "Starting Celery worker..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; celery -A backend.workers.celery_app.celery_app worker -l info --pool=solo -Q dataset_generation,celery"

Write-Host "Done! Backend at http://localhost:8000" -ForegroundColor Green
