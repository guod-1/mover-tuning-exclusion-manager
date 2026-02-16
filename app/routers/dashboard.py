from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.ca_mover import get_mover_parser
from app.services.exclusions import get_exclusion_manager
from app.services.radarr import get_radarr_client
from app.services.sonarr import get_sonarr_client
import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    mover = get_mover_parser()
    excl = get_exclusion_manager()
    
    # Test connections
    radarr_connected = get_radarr_client().test_connection()
    sonarr_connected = get_sonarr_client().test_connection()
    
    # Get stats
    mover_stats = mover.get_latest_stats()
    excl_stats = excl.get_exclusion_stats()
    
    last_check = "N/A"
    status_text = "No logs found"
    if mover_stats:
        status_text = f"{mover_stats['excluded']} Excluded / {mover_stats['moved']} Moved"
        last_check = datetime.datetime.fromtimestamp(mover_stats['timestamp']).strftime('%Y-%m-%d %H:%M')
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "radarr_connected": radarr_connected,
        "sonarr_connected": sonarr_connected,
        "ca_mover_status": status_text,
        "exclusion_count": excl_stats.get("total_count", 0),
        "last_run_mover": last_check
    })
