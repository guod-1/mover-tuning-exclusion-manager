import logging
from pathlib import Path
from typing import List, Set
from app.core.config import get_user_settings
from app.services.radarr import get_radarr_client
from app.services.sonarr import get_sonarr_client

logger = logging.getLogger(__name__)

class ExclusionManager:
    def __init__(self):
        self.settings = get_user_settings()
        self.output_file = Path("/config/mover_exclusions.txt")

    def _normalize_path(self, path: str) -> str:
        """
        Forces paths to match the strict /mnt/chloe/data/media structure.
        """
        if not path:
            return ""
        
        # Clean up whitespace and quotes
        clean_path = path.strip().strip('"').strip("'")
        
        # If it's already a full host path, leave it
        if clean_path.startswith("/mnt/chloe/data/media/"):
            return clean_path

        # Logic for Movies: Extract part after 'movies'
        if "/movies/" in clean_path.lower():
            try:
                # find index regardless of case
                idx = clean_path.lower().find("/movies/")
                relative_part = clean_path[idx + 8:] # skip '/movies/'
                return f"/mnt/chloe/data/media/movies/{relative_part}"
            except: pass

        # Logic for TV: Extract part after 'tv'
        if "/tv/" in clean_path.lower():
            try:
                idx = clean_path.lower().find("/tv/")
                relative_part = clean_path[idx + 4:] # skip '/tv/'
                return f"/mnt/chloe/data/media/tv/{relative_part}"
            except: pass

        # Special Case: If it's just a folder like /chloe/tv/...
        if clean_path.startswith("/chloe/"):
             return clean_path.replace("/chloe/", "/mnt/chloe/data/media/", 1)

        return clean_path

    def combine_exclusions(self) -> int:
        all_paths = set()

        # ---------------------------------------------------------
        # A. Manual Folder Exclusions
        # ---------------------------------------------------------
        if self.settings.exclusions.custom_folders:
            for folder in self.settings.exclusions.custom_folders:
                all_paths.add(self._normalize_path(folder))

        # ---------------------------------------------------------
        # B. PlexCache-D Exclusions
        # ---------------------------------------------------------
        plex_cache_file = Path(self.settings.exclusions.plexcache_file_path)
        if plex_cache_file.exists():
            try:
                with open(plex_cache_file, 'r') as f:
                    for line in f:
                        clean = line.strip()
                        # Skip empty lines and comments
                        if not clean or clean.startswith('#'):
                            continue
                        
                        # Add the normalized path
                        normalized = self._normalize_path(clean)
                        all_paths.add(normalized)
                logger.info(f"Integrated exclusions from {plex_cache_file}")
            except Exception as e:
                logger.error(f"Error reading PlexCache file: {e}")
        else:
            logger.warning(f"PlexCache file not found at: {plex_cache_file}")

        # ---------------------------------------------------------
        # C. Tags (Radarr/Sonarr)
        # ---------------------------------------------------------
        target_tags = set(self.settings.exclusions.exclude_tag_ids)
        if target_tags:
            # Add Radarr Files
            try:
                radarr = get_radarr_client()
                movies = radarr.get_all_movies()
                for m in movies:
                    if m.get('hasFile') and any(t in target_tags for t in m.get('tags', [])):
                        movie_file = m.get('movieFile')
                        if movie_file:
                            all_paths.add(self._normalize_path(movie_file['path']))
            except Exception as e: logger.error(f"Radarr fetch failed: {e}")

            # Add Sonarr Files
            try:
                sonarr = get_sonarr_client()
                shows = sonarr.get_all_shows()
                for s in shows:
                    if any(t in target_tags for t in s.get('tags', [])):
                        ep_files = sonarr.get_episode_files(s['id'])
                        for ep in ep_files:
                            all_paths.add(self._normalize_path(ep['path']))
            except Exception as e: logger.error(f"Sonarr fetch failed: {e}")

        # Write to final file
        try:
            # Filter out any empty strings and sort
            final_list = sorted([p for p in all_paths if p])
            with open(self.output_file, 'w') as f:
                for path in final_list:
                    f.write(f"{path}\n")
            logger.info(f"Wrote {len(final_list)} total paths to {self.output_file}")
            return len(final_list)
        except Exception as e:
            logger.error(f"Failed to write exclusion file: {e}")
            return 0

    def get_exclusion_stats(self) -> dict:
        if not self.output_file.exists():
            return {"total_count": 0}
        try:
            with open(self.output_file, 'r') as f:
                return {"total_count": len([l for l in f if l.strip()])}
        except:
            return {"total_count": 0}

def get_exclusion_manager():
    return ExclusionManager()
