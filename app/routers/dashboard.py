from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.config import get_user_settings
from app.services.ca_mover import get_mover_parser

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    settings = get_user_settings()
    parser = get_mover_parser()
    stats = parser.get_latest_stats()
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "settings": settings, 
        "stats": stats
    })
