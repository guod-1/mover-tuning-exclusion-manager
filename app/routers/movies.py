"""
Movies Router

Display and manage movies
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging

from app.services.radarr import get_radarr_client
from app.core.config import get_user_settings

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def movies_page(request: Request):
    """Movies listing page"""
    
    user_settings = get_user_settings()
    radarr_client = get_radarr_client()
    
    # Only fetch movies if tag operation is configured
    movies = []
    if user_settings.radarr_tag_operation.search_tag_id:
        try:
            movie_ids = radarr_client.get_movie_ids_by_tag(user_settings.radarr_tag_operation.search_tag_id)
            
            for movie_id in movie_ids[:50]:  # Limit to 50 for now
                try:
                    movie = radarr_client.get_movie(movie_id)
                    if movie:
                        ratings = {
                            'imdb': movie.get('ratings', {}).get('imdb', {}).get('value', 0),
                            'tmdb': movie.get('ratings', {}).get('tmdb', {}).get('value', 0)
                        }
                        
                        movies.append({
                            'id': movie_id,
                            'title': movie.get('title', 'Unknown'),
                            'year': movie.get('year', ''),
                            'ratings': ratings,
                            'tags': movie.get('tags', [])
                        })
                except Exception as e:
                    logger.error(f"Error fetching movie {movie_id}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error fetching movies: {e}")
    
    context = {
        "request": request,
        "movies": movies
    }
    
    return templates.TemplateResponse("movies.html", context)


@router.get("/api/list")
async def get_movies_api():
    """API endpoint for movies list"""
    
    user_settings = get_user_settings()
    radarr_client = get_radarr_client()
    
    if not user_settings.radarr_tag_operation.search_tag_id:
        return {"success": False, "error": "No search tag configured"}
    
    try:
        movie_ids = radarr_client.get_movie_ids_by_tag(user_settings.radarr_tag_operation.search_tag_id)
        
        movies = []
        for movie_id in movie_ids:
            try:
                movie = radarr_client.get_movie(movie_id)
                if movie:
                    ratings = {
                        'imdb': movie.get('ratings', {}).get('imdb', {}).get('value', 0),
                        'tmdb': movie.get('ratings', {}).get('tmdb', {}).get('value', 0)
                    }
                    
                    movies.append({
                        'id': movie_id,
                        'title': movie.get('title', 'Unknown'),
                        'year': movie.get('year', ''),
                        'ratings': ratings
                    })
            except:
                continue
        
        return {"success": True, "movies": movies}
    
    except Exception as e:
        logger.error(f"Error fetching movies: {e}")
        return {"success": False, "error": str(e)}
