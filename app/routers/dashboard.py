from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.ca_mover import get_mover_parser
from app.services.exclusions import get_exclusion_manager
import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    mover_parser = get_mover_parser()
    exclusion_manager = get_exclusion_manager()
    
    # Get stats with absolute fallbacks
    stats = mover_parser.get_latest_stats() or {
        "excluded": 0, "moved": 0, "filename": "No logs found", "timestamp": 0
    }
    
    cache_usage = mover_parser.get_cache_usage() or {
        "percent": 0, "used": 0, "total": 1
    }
    
    exclusion_stats = exclusion_manager.get_exclusion_stats() or {"total_count": 0}
    
    # Manual Check for Radarr/Sonarr connectivity
    from app.services.radarr import get_radarr_client
    from app.services.sonarr import get_sonarr_client
    
    radarr_online = False
    try:
        radarr_online = bool(get_radarr_client().get_all_movies())
    except: pass
    
    sonarr_online = False
    try:
        sonarr_online = bool(get_sonarr_client().get_all_series())
    except: pass

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "cache_usage": cache_usage,
        "exclusion_count": exclusion_stats.get("total_count", 0),
        "radarr_online": radarr_online,
        "sonarr_online": sonarr_online,
        "check_time": datetime.datetime.now().strftime("%H:%M:%S")
    })

@router.get("/stats/refresh", response_class=HTMLResponse)
async def refresh_stats(request: Request):
    mover_parser = get_mover_parser()
    stats = mover_parser.get_latest_stats() or {"excluded": 0, "moved": 0, "filename": "No logs found"}
    return templates.TemplateResponse("partials/mover_stats_card.html", {
        "request": request, 
        "stats": stats, 
        "check_time": datetime.datetime.now().strftime("%H:%M:%S")
    })
