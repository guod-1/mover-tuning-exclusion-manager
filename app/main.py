import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import dashboard, movies, shows, exclusions, settings, logs, stats, operations
from app.core.scheduler import scheduler_service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("/config/app.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mover Tuning Exclusion Manager")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers - ensuring the dashboard doesn't clash
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(movies.router, prefix="/movies", tags=["Movies"])
app.include_router(shows.router, prefix="/shows", tags=["Shows"])
app.include_router(exclusions.router, prefix="/exclusions", tags=["Exclusions"])
app.include_router(settings.router, prefix="/settings", tags=["Settings"])
app.include_router(logs.router, prefix="/logs", tags=["Logs"])
app.include_router(stats.router, prefix="/stats", tags=["Stats"])
app.include_router(operations.router, prefix="/operations", tags=["Operations"])

@app.get("/")
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard")

@app.on_event("startup")
async def startup_event():
    scheduler_service.start()
    logger.info("Mover Tuning Exclusion Manager started and scheduler initialized.")
