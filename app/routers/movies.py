"""
Movies Router
Display movies from Radarr with specific tags
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
async def movies_page(request: Request):
    """Movies listing page"""
    user_settings = get_user_settings()
    radarr_client = get_radarr_client()
    
    movies = []
    tag_id = user_settings.radarr_tag_operation.search_tag_id
    
    if tag_id:
        try:
            movie_ids = radarr_client.get_movie_ids_by_tag(tag_id)
            
            for movie_id in movie_ids:
                movie = radarr_client.get_movie(movie_id)
                if movie:
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
        "tag_id": tag_id,
        "total": len(movies)
    }
    
    return templates.TemplateResponse("movies.html", context)
