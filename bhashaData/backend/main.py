# Artha AI Backend v2.2 - 2026-04-13

import asyncio
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router as api_router
from backend.database import models  # noqa: F401
from backend.database.db import Base, engine
from backend.config.settings import settings


logger = logging.getLogger(__name__)

app = FastAPI(title="Artha AI", version="1.0.0")

# Configure CORS for development and production
allow_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

# Add production frontend URL if provided
if settings.frontend_url and settings.frontend_url not in allow_origins:
    allow_origins.append(settings.frontend_url)

# Add Vercel deployments
allow_origins.append("https://*.vercel.app")

# Filter out empty strings
allow_origins = [origin for origin in allow_origins if origin]

app.add_middleware(
	CORSMiddleware,
	allow_origins=allow_origins,
	allow_origin_regex=r"https://.*\.vercel\.app",
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
	try:
		port = os.getenv("PORT", "8000")
		logger.info(f"Starting on PORT: {port}")
		await asyncio.wait_for(
			asyncio.get_event_loop().run_in_executor(
				None,
				lambda: Base.metadata.create_all(bind=engine),
			),
			timeout=30.0,
		)
		logger.info("Artha AI backend started")
	except asyncio.TimeoutError:
		logger.warning("DB init timed out — continuing anyway")
	except Exception as e:
		logger.warning(f"DB init error: {e} — continuing")


@app.on_event("shutdown")
def shutdown_event() -> None:
	logger.info("Artha AI shutting down")


app.include_router(api_router, prefix="/api")
