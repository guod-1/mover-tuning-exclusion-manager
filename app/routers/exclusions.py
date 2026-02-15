"""
Exclusions Router

View and manage exclusion files
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
import logging
from pathlib import Path

from app.core.config import get_settings, get_user_settings
from app.services.exclusions import get_exclusion_manager
from app.services.radarr import get_radarr_client

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def exclusions_page(request: Request):
    """Exclusions viewing page"""
    
    settings = get_settings()
    user_settings = get_user_settings()
    exclusion_manager = get_exclusion_manager()
    radarr_client = get_radarr_client()
    
    # Get available tags from Radarr
    tags = []
    try:
        if user_settings.radarr.api_key:
            tags = radarr_client.get_all_tags()
    except Exception as e:
        logger.error(f"Failed to fetch tags: {e}")
    
    # Read exclusions file
    exclusions = []
    if settings.exclusions_file.exists():
        try:
            with open(settings.exclusions_file, 'r') as f:
                exclusions = [line.strip() for line in f if line.strip()]
        except Exception as e:
            logger.error(f"Error reading exclusions: {e}")
    
    # Get stats
    stats = exclusion_manager.get_exclusion_stats()
    
    context = {
        "request": request,
        "user_settings": user_settings,
        "tags": tags,
        "exclusions": exclusions,
        "total": stats['total'],
        "files": stats['files'],
        "directories": stats['directories'],
        "output_path": str(settings.exclusions_file)
    }
    
    return templates.TemplateResponse("exclusions.html", context)


@router.get("/download", response_class=PlainTextResponse)
async def download_exclusions():
    """Download the exclusions file"""
    
    settings = get_settings()
    
    try:
        if settings.exclusions_file.exists():
            with open(settings.exclusions_file, 'r') as f:
                content = f.read()
            return PlainTextResponse(
                content=content,
                headers={"Content-Disposition": "attachment; filename=mover_exclusions.txt"}
            )
        else:
            return PlainTextResponse("Exclusions file not found", status_code=404)
    except Exception as e:
        logger.error(f"Error reading exclusions: {e}")
        return PlainTextResponse(f"Error: {str(e)}", status_code=500)
