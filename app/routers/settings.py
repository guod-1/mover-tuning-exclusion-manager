from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import logging
from app.core.config import (
    get_user_settings, save_user_settings,
    RadarrSettings, SonarrSettings, RadarrTagOperation, SonarrTagOperation,
    ExclusionSettings, SchedulerSettings
)
from app.services.radarr import get_radarr_client
from app.services.sonarr import get_sonarr_client

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def settings_page(request: Request):
    user_settings = get_user_settings()
    
    # Initialize empty lists
    radarr_tags = []
    sonarr_tags = []
    
    # Try to fetch actual tags from the APIs
    try:
        radarr_tags = get_radarr_client().get_all_tags()
    except Exception as e:
        logger.warning(f"Could not load Radarr tags for settings: {e}")
        
    try:
        sonarr_tags = get_sonarr_client().get_all_tags()
    except Exception as e:
        logger.warning(f"Could not load Sonarr tags for settings: {e}")

    return templates.TemplateResponse("settings.html", {
        "request": request,
        "settings": user_settings,
        "radarr_tags": radarr_tags,
        "sonarr_tags": sonarr_tags
    })

@router.post("/radarr-tags")
async def update_radarr_tags(radarr_search_tag_id: str = Form(""), radarr_replace_tag_id: str = Form("")):
    user_settings = get_user_settings()
    s_id = int(radarr_search_tag_id) if radarr_search_tag_id.strip() else None
    r_id = int(radarr_replace_tag_id) if radarr_replace_tag_id.strip() else None
    user_settings.radarr_tag_operation = RadarrTagOperation(search_tag_id=s_id, replace_tag_id=r_id)
    save_user_settings(user_settings)
    return RedirectResponse(url="/settings/?success=radarr_tags", status_code=303)

@router.post("/sonarr-tags")
async def update_sonarr_tags(sonarr_search_tag_id: str = Form(""), sonarr_replace_tag_id: str = Form("")):
    user_settings = get_user_settings()
    s_id = int(sonarr_search_tag_id) if sonarr_search_tag_id.strip() else None
    r_id = int(sonarr_replace_tag_id) if sonarr_replace_tag_id.strip() else None
    user_settings.sonarr_tag_operation = SonarrTagOperation(search_tag_id=s_id, replace_tag_id=r_id)
    save_user_settings(user_settings)
    return RedirectResponse(url="/settings/?success=sonarr_tags", status_code=303)
