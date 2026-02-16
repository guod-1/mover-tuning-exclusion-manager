"""
Shows Router
Display all TV shows from Sonarr
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging

from app.services.sonarr import get_sonarr_client

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def shows_page(request: Request):
    """Shows listing page - shows all TV shows from Sonarr"""
    sonarr_client = get_sonarr_client()
    
    shows = []
    
    try:
        # Get all series from Sonarr
        all_series = sonarr_client.get_all_series()
        
        for series in all_series:
            shows.append({
                'id': series['id'],
                'title': series['title'],
                'year': series.get('year', 'N/A'),
                'path': series.get('path', ''),
                'status': series.get('status', 'Unknown'),
                'seasons': series.get('seasonCount', 0)
            })
    except Exception as e:
        logger.error(f"Failed to fetch shows: {e}")
    
    context = {
        "request": request,
        "shows": shows,
        "total": len(shows)
    }
    
    return templates.TemplateResponse("shows.html", context)
