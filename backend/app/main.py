from fastapi import FastAPI

from app.api.health import router as health_router

app = FastAPI(title="MO4 Light Interface")

# Served at /health (local) and /api/health (Vercel keeps the /api prefix).
app.include_router(health_router)
app.include_router(health_router, prefix="/api")
