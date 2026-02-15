from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.ca_mover import get_mover_parser
from app.services.exclusions import get_exclusion_manager
import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Register the missing 'datetime' filter
def format_datetime(value):
    if value is None:
        return ""
    return datetime.datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')

templates.env.filters["datetime"] = format_datetime

@router.get("/", response_class=HTMLResponse)
async def stats_page(request: Request):
    mover = get_mover_parser()
    excl = get_exclusion_manager()
    
    mover_stats = mover.get_latest_stats()
    excl_stats = excl.get_exclusion_stats()
    
    return templates.TemplateResponse("stats.html", {
        "request": request,
        "mover": mover_stats,
        "exclusions": excl_stats
    })
