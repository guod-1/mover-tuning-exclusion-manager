import logging
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from app.core.config import get_user_settings
from app.core.scheduler import get_scheduler
from app.routers import dashboard, settings, movies, shows, logs, operations, exclusions

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mover Tuning Exclusion Manager")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(dashboard.router, tags=["Dashboard"])
app.include_router(exclusions.router, prefix="/exclusions", tags=["Exclusions"])
app.include_router(movies.router, prefix="/movies", tags=["Movies"])
app.include_router(shows.router, prefix="/shows", tags=["Shows"])
app.include_router(settings.router, prefix="/settings", tags=["Settings"])
app.include_router(logs.router, prefix="/logs", tags=["Logs"])
app.include_router(operations.router, prefix="/operations", tags=["Operations"])

@app.on_event("startup")
async def startup_event():
    user_settings = get_user_settings()
    logger.info("Starting Mover Tuning Exclusion Manager...")
    logger.info(f"Config directory: /config")
    
    # Start the scheduler
    scheduler = get_scheduler()
    scheduler.start()
    logger.info("Scheduler started")

@app.on_event("shutdown")
async def shutdown_event():
    scheduler = get_scheduler()
    scheduler.shutdown()
    logger.info("Shutting down...")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return RedirectResponse(url="/")

