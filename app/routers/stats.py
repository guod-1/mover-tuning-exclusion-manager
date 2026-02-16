from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.ca_mover import get_mover_parser

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
async def stats_page(request: Request):
    mover_parser = get_mover_parser()
    stats = mover_parser.get_latest_stats()
    return templates.TemplateResponse("stats.html", {
        "request": request,
        "stats": stats
    })
