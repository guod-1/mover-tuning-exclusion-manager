"""
Movies Router
Display all movies from Radarr
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging

from app.services.radarr import get_radarr_client

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def movies_page(request: Request):
    """Movies listing page - shows all movies from Radarr"""
    radarr_client = get_radarr_client()
    
    movies = []
    
    try:
        # Get all movies from Radarr
        all_movies = radarr_client.get_all_movies()
        
        for movie in all_movies:
            movies.append({
                'id': movie['id'],
                'title': movie['title'],
                'year': movie.get('year', 'N/A'),
                'path': movie.get('path', ''),
                'status': movie.get('status', 'Unknown'),
                'hasFile': movie.get('hasFile', False)
            })
    except Exception as e:
        logger.error(f"Failed to fetch movies: {e}")
    
    context = {
        "request": request,
        "movies": movies,
        "total": len(movies)
    }
    
    return templates.TemplateResponse("movies.html", context)
