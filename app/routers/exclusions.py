from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.core.config import get_user_settings, save_user_settings, ExclusionSettings
from app.services.radarr import get_radarr_client
from app.services.sonarr import get_sonarr_client
from app.services.exclusions import get_exclusion_manager
import logging
from typing import List

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def exclusions_page(request: Request):
    """Exclusions management page"""
    user_settings = get_user_settings()
    
    # Get tags from both services
    radarr_client = get_radarr_client()
    sonarr_client = get_sonarr_client()
    
    tags = []
    sonarr_tags = []
    
    try:
        tags = radarr_client.get_all_tags()
    except Exception as e:
        logger.error(f"Failed to fetch Radarr tags: {e}")
    
    try:
        sonarr_tags = sonarr_client.get_all_tags()
    except Exception as e:
        logger.error(f"Failed to fetch Sonarr tags: {e}")
    
    # Get exclusion stats and content
    excl_manager = get_exclusion_manager()
    stats = excl_manager.get_exclusion_stats()
    exclusions = []
    
    try:
        with open("/config/mover_exclusions.txt", "r") as f:
            exclusions = [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Failed to read exclusions file: {e}")
    
    context = {
        "request": request,
        "user_settings": user_settings,
        "tags": tags,
        "sonarr_tags": sonarr_tags,
        "stats": stats,
        "exclusions": exclusions
    }
    
    return templates.TemplateResponse("exclusions.html", context)


@router.post("/settings")
async def save_exclusion_settings(
    custom_folders: str = Form(""),
    radarr_exclude_tag_ids: List[int] = Form([]),
    sonarr_exclude_tag_ids: List[int] = Form([]),
    plexcache_file_path: str = Form("/plexcache/unraid_mover_exclusions.txt"),
    ca_mover_log_path: str = Form("/config/ca.mover.tuning")
):
    """Save all exclusion settings"""
    # Parse custom folders
    folder_list = [f.strip() for f in custom_folders.split('\n') if f.strip()]
    
    user_settings = get_user_settings()
    user_settings.exclusions = ExclusionSettings(
        custom_folders=folder_list,
        radarr_exclude_tag_ids=radarr_exclude_tag_ids,
        sonarr_exclude_tag_ids=sonarr_exclude_tag_ids,
        plexcache_file_path=plexcache_file_path,
        ca_mover_log_path=ca_mover_log_path
    )
    
    save_user_settings(user_settings)
    logger.info(f"Exclusion settings saved: {len(radarr_exclude_tag_ids)} Radarr tags, {len(sonarr_exclude_tag_ids)} Sonarr tags, {len(folder_list)} custom folders")
    
    return RedirectResponse(url="/exclusions/?success=true", status_code=303)
