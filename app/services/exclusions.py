import logging
import os
from pathlib import Path
from app.core.config import get_user_settings
from app.services.radarr import get_radarr_client
from app.services.sonarr import get_sonarr_client

# Set level to INFO specifically for this module to ensure we see these logs
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ExclusionManager:
    def __init__(self):
        self.output_file = Path("/config/mover_exclusions.txt")

    def _normalize_path(self, path: str) -> str:
        if not path: return ""
        clean = path.strip().strip('"').strip("'")
        low_path = clean.lower()
        
        if "/movies/" in low_path:
            idx = low_path.find("/movies/")
            return f"/mnt/chloe/data/media/movies/{clean[idx+8:]}"
        if "/tv/" in low_path:
            idx = low_path.find("/tv/")
            return f"/mnt/chloe/data/media/tv/{clean[idx+4:]}"
        return clean

    def combine_exclusions(self) -> int:
        logger.info("!!! STARTING EXCLUSION COMBINATION PROCESS !!!")
        all_paths = set()
        settings = get_user_settings()

        # 1. Manual Folders
        logger.info(f"Checking {len(settings.exclusions.custom_folders)} manual folders")
        for folder in settings.exclusions.custom_folders:
            all_paths.add(self._normalize_path(folder))

        # 2. PlexCache File
        pc_path_str = settings.exclusions.plexcache_file_path
        logger.info(f"Checking PlexCache file at: {pc_path_str}")
        pc_path = Path(pc_path_str)
        
        if pc_path.exists():
            try:
                with open(pc_path, 'r') as f:
                    lines = [l for l in f.readlines() if l.strip() and not l.startswith('#')]
                    logger.info(f"FOUND PlexCache file. Parsing {len(lines)} lines.")
                    for line in lines:
                        normalized = self._normalize_path(line)
                        all_paths.add(normalized)
            except Exception as e:
                logger.error(f"ERROR reading PlexCache: {e}")
        else:
            logger.warning(f"PLEXCACHE FILE NOT FOUND: {pc_path_str}")

        # 3. Tags
        target_tags = set(settings.exclusions.exclude_tag_ids)
        logger.info(f"Target Tags set in UI: {target_tags}")
        if target_tags:
            try:
                radarr = get_radarr_client()
                movies = radarr.get_all_movies()
                logger.info(f"Fetched {len(movies)} movies from Radarr to check for tags")
                for m in movies:
                    m_tags = m.get('tags', [])
                    if m.get('hasFile') and any(t in target_tags for t in m_tags):
                        path = m['movieFile']['path']
                        all_paths.add(self._normalize_path(path))
            except Exception as e:
                logger.error(f"Radarr tag check failed: {e}")

        # 4. Final Write
        final_list = sorted([p for p in all_paths if p])
        logger.info(f"FINAL LIST: {len(final_list)} items total.")
        
        try:
            with open(self.output_file, 'w') as f:
                for path in final_list:
                    f.write(f"{path}\n")
            logger.info(f"!!! SUCCESS !!! Wrote to {self.output_file}")
            return len(final_list)
        except Exception as e:
            logger.error(f"CRITICAL: Failed to write {self.output_file}: {e}")
            return 0

    def get_exclusion_stats(self) -> dict:
        if not self.output_file.exists(): return {"total_count": 0}
        try:
            with open(self.output_file, 'r') as f:
                count = len([l for l in f if l.strip()])
                return {"total_count": count}
        except: return {"total_count": 0}

def get_exclusion_manager():
    return ExclusionManager()
