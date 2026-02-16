"""
Shows Router
Display TV shows from Sonarr with search and tags
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging

from app.core.config import get_user_settings
from app.services.sonarr import get_sonarr_client

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def shows_page(request: Request, q: str = ""):
    """Shows listing page with search and tags"""
    user_settings = get_user_settings()
    sonarr_client = get_sonarr_client()
    
    shows = []
    tag_map = {}
    
    try:
        # 1. Fetch all tags
        all_tags = sonarr_client.get_all_tags()
        tag_map = {t['id']: t['label'] for t in all_tags}
        
        # 2. Fetch all series
        all_series = sonarr_client.get_all_series()
        
        # 3. Filter and Format
        for s in all_series:
            # Search Filter
            if q and q.lower() not in s['title'].lower():
                continue
            
            # Resolve Tags
            show_tag_labels = [tag_map.get(tid, str(tid)) for tid in s.get('tags', [])]
            
            shows.append({
                'id': s['id'],
                'title': s['title'],
                'year': s.get('year', 'N/A'),
                'path': s.get('path', ''),
                'status': s.get('status', 'Unknown'),
                'seasons': s.get('seasonCount', 0),
                'tags': show_tag_labels
            })
            
    except Exception as e:
        logger.error(f"Failed to fetch shows: {e}")
    
    context = {
        "request": request,
        "shows": shows[:200] if not q else shows, # Limit default view
        "total": len(shows),
        "search_query": q
    }
    
    return templates.TemplateResponse("shows.html", context)
