from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
import os
import logging
from app.core.config import get_user_settings

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def logs_page(request: Request):
    log_content = ""
    log_path = "/config/app.log"
    if os.path.exists(log_path):
        try:
            with open(log_path, "r") as f:
                # Read last 200 lines for the UI
                log_content = "".join(f.readlines()[-200:])
        except Exception as e:
            log_content = f"Error reading logs: {e}"
    else:
        log_content = "No log file found yet."

    return templates.TemplateResponse("logs.html", {
        "request": request,
        "logs": log_content
    })

@router.get("/download")
async def download_logs():
    log_path = "/config/app.log"
    if os.path.exists(log_path):
        return FileResponse(log_path, filename="mover_manager.log")
    return {"error": "Log file not found"}

@router.post("/clear", response_class=HTMLResponse)
async def clear_logs():
    log_path = "/config/app.log"
    if os.path.exists(log_path):
        with open(log_path, "w") as f:
            f.write("")
    return '<div class="bg-green-100 border border-green-400 text-green-700 px-4 py-2 rounded mb-4">Logs cleared successfully</div>'
