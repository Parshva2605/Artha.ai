import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router as api_router
from backend.database import models  # noqa: F401
from backend.database.db import Base, engine


logger = logging.getLogger(__name__)

app = FastAPI(title="Artha AI", version="1.0.0")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:3000", "http://localhost:3001"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
	Base.metadata.create_all(bind=engine)
	logger.info("Artha AI backend started")


@app.on_event("shutdown")
def shutdown_event() -> None:
	logger.info("Artha AI shutting down")


app.include_router(api_router, prefix="/api")
