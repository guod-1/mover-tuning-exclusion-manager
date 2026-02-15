import logging
import os
from pathlib import Path
from app.core.config import get_user_settings
from app.services.radarr import get_radarr_client
from app.services.sonarr import get_sonarr_client

logger = logging.getLogger(__name__)

class ExclusionManager:
    def __init__(self):
        self.output_file = Path("/config/mover_exclusions.txt")

    def _normalize_path(self, path: str) -> str:
        if not path: return ""
        clean = path.strip().strip('"').strip("'")
        low_path = clean.lower()
        
        # MOVIE LOGIC: Adjusting to ensure the file-level mapping is correct
        if "/movies/" in low_path:
            idx = low_path.find("/movies/")
            # Extract the portion after /movies/
            movie_part = clean[idx+8:]
            # If you need a specific hyphenation or structure change here, 
            # this is where we apply it. Currently forcing the /mnt/chloe prefix:
            return f"/mnt/chloe/data/media/movies/{movie_part}"
            
        # TV LOGIC (Staying as is since you confirmed it was correct)
        if "/tv/" in low_path:
            idx = low_path.find("/tv/")
            return f"/mnt/chloe/data/media/tv/{clean[idx+4:]}"
        
        return clean

    def combine_exclusions(self) -> int:
        logger.info("!!! STARTING EXCLUSION COMBINATION PROCESS !!!")
        all_paths = set()
        settings = get_user_settings()

        # 1. Manual Folders
        for folder in settings.exclusions.custom_folders:
            all_paths.add(self._normalize_path(folder))

        # 2. PlexCache / unraid_mover_exclusions.txt
        pc_path_str = settings.exclusions.plexcache_file_path
        pc_path = Path(pc_path_str)
        
        if not pc_path.exists() and pc_path.parent.exists():
            search_name = "unraid_mover_exclusions.txt"
            if os.path.exists(pc_path.parent / search_name):
                pc_path = pc_path.parent / search_name

        if pc_path.exists() and pc_path.is_file():
            try:
                with open(pc_path, 'r') as f:
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            all_paths.add(self._normalize_path(line))
                logger.info(f"Integrated lines from {pc_path}")
            except Exception as e:
                logger.error(f"Error reading plexcache file: {e}")

        # 3. Tags
        target_tags = set(settings.exclusions.exclude_tag_ids)
        if target_tags:
            try:
                radarr = get_radarr_client()
                movies = radarr.get_all_movies()
                for m in movies:
                    if m.get('hasFile') and any(t in target_tags for t in m.get('tags', [])):
                        # Fix for movies: ensuring we grab the file path
                        if 'movieFile' in m and 'path' in m['movieFile']:
                            all_paths.add(self._normalize_path(m['movieFile']['path']))
            except Exception as e:
                logger.error(f"Radarr tag check failed: {e}")

        # 4. Final Write
        final_list = sorted([p for p in all_paths if p])
        with open(self.output_file, 'w') as f:
            for path in final_list:
                f.write(f"{path}\n")
        logger.info(f"!!! COMPLETED !!! Total items: {len(final_list)}")
        return len(final_list)

    def get_exclusion_stats(self) -> dict:
        if not self.output_file.exists(): return {"total_count": 0}
        with open(self.output_file, 'r') as f:
            return {"total_count": len([l for l in f if l.strip()])}

def get_exclusion_manager():
    return ExclusionManager()
