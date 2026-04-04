from fastapi import FastAPI

from api.routes import router as api_router

app = FastAPI(title="BhashaData API", version="1.0")
app.include_router(api_router, prefix="/api")
