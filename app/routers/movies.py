"""
Movies Router
Display movies from Radarr with search and tags
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging

from app.core.config import get_user_settings
from app.services.radarr import get_radarr_client

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def movies_page(request: Request, q: str = ""):
    """Movies listing page with search and tags"""
    user_settings = get_user_settings()
    radarr_client = get_radarr_client()
    
    movies = []
    tag_map = {}
    
    try:
        # 1. Fetch all tags to create a lookup dict (ID -> Label)
        all_tags = radarr_client.get_all_tags()
        tag_map = {t['id']: t['label'] for t in all_tags}
        
        # 2. Fetch movies (If searching, we filter in memory for now as Radarr API search is complex)
        # Note: For large libraries, we might want to use Radarr's lookup, but get_all_movies is standard.
        all_movies = radarr_client.get_all_movies()
        
        # 3. Filter and Format
        for m in all_movies:
            # Search Filter
            if q and q.lower() not in m['title'].lower():
                continue
                
            # Resolve Tags
            movie_tag_labels = [tag_map.get(tid, str(tid)) for tid in m.get('tags', [])]
            
            movies.append({
                'id': m['id'],
                'title': m['title'],
                'year': m.get('year', 'N/A'),
                'path': m.get('path', ''),
                'status': m.get('status', 'Unknown'),
                'hasFile': m.get('hasFile', False),
                'tags': movie_tag_labels
            })
            
    except Exception as e:
        logger.error(f"Failed to fetch movies: {e}")
    
    context = {
        "request": request,
        "movies": movies[:200] if not q else movies, # Limit default view to 200 for speed
        "total": len(movies),
        "search_query": q
    }
    
    return templates.TemplateResponse("movies.html", context)
