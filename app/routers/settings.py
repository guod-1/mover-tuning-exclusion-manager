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
from app.core.scheduler import get_scheduler

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def settings_page(request: Request):
    user_settings = get_user_settings()
    
    radarr_tags = []
    sonarr_tags = []
    
    try:
        radarr_tags = get_radarr_client().get_all_tags()
    except Exception:
        pass
        
    try:
        sonarr_tags = get_sonarr_client().get_all_tags()
    except Exception:
        pass

    return templates.TemplateResponse("settings.html", {
        "request": request,
        "settings": user_settings,
        "radarr_tags": radarr_tags,
        "sonarr_tags": sonarr_tags
    })

# --- Radarr Connection ---
@router.post("/radarr")
async def update_radarr(url: str = Form(...), api_key: str = Form(...)):
    user_settings = get_user_settings()
    user_settings.radarr = RadarrSettings(url=url, api_key=api_key)
    save_user_settings(user_settings)
    return RedirectResponse(url="/settings/?success=radarr", status_code=303)

@router.post("/radarr/test")
async def test_radarr():
    try:
        connected = get_radarr_client().test_connection()
        return {"success": connected, "message": "Connected successfully!" if connected else "Connection failed"}
    except Exception as e:
        return {"success": False, "message": str(e)}

# --- Sonarr Connection ---
@router.post("/sonarr")
async def update_sonarr(url: str = Form(...), api_key: str = Form(...)):
    user_settings = get_user_settings()
    user_settings.sonarr = SonarrSettings(url=url, api_key=api_key)
    save_user_settings(user_settings)
    return RedirectResponse(url="/settings/?success=sonarr", status_code=303)

@router.post("/sonarr/test")
async def test_sonarr():
    try:
        connected = get_sonarr_client().test_connection()
        return {"success": connected, "message": "Connected successfully!" if connected else "Connection failed"}
    except Exception as e:
        return {"success": False, "message": str(e)}

# --- Tag Operations ---
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

# --- Scheduler ---
@router.post("/scheduler")
async def update_scheduler(
    enabled: bool = Form(False),
    cron_expression: str = Form(...),
    ca_mover_check_cron: str = Form("30 23 * * *")
):
    user_settings = get_user_settings()
    clean_cron = cron_expression.replace('"', '').replace("'", "")
    clean_check = ca_mover_check_cron.replace('"', '').replace("'", "")
    
    user_settings.scheduler = SchedulerSettings(
        enabled=enabled,
        cron_expression=clean_cron,
        ca_mover_check_cron=clean_check
    )
    save_user_settings(user_settings)
    
    scheduler = get_scheduler()
    scheduler.update_schedule()
    
    return RedirectResponse(url="/settings/?success=scheduler", status_code=303)
