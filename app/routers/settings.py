from app.core.scheduler import scheduler_service
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from app.core.config import get_user_settings, save_user_settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/paths/save")
async def save_paths(
    cache_mount_path: str = Form(...),
    movie_base_path: str = Form(...), 
    tv_base_path: str = Form(...),
    ca_mover_log_path: str = Form(...),
    full_sync_cron: str = Form(...),
    log_monitor_cron: str = Form(...)
):
    settings = get_user_settings()
    settings.exclusions.cache_mount_path = cache_mount_path
    settings.exclusions.movie_base_path = movie_base_path
    settings.exclusions.tv_base_path = tv_base_path
    settings.exclusions.ca_mover_log_path = ca_mover_log_path
    settings.exclusions.full_sync_cron = full_sync_cron
    settings.exclusions.log_monitor_cron = log_monitor_cron
    save_user_settings(settings)
    scheduler_service.reload_jobs()
    return RedirectResponse(url="/settings?status=success", status_code=303)
# ... other routes remained the same ...
