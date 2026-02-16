import os
import logging
import shutil
from app.core.config import get_user_settings

logger = logging.getLogger(__name__)

class MoverLogParser:
    def __init__(self, log_dir="/mover_logs"):
        self.log_dir = log_dir

    def get_cache_usage(self):
        try:
            settings = get_user_settings()
            path = settings.exclusions.cache_mount_path
            if not path or not os.path.exists(path):
                return {"total": 1, "used": 0, "free": 0, "percent": 0}
            usage = shutil.disk_usage(path)
            percent = (usage.used / usage.total) * 100 if usage.total > 0 else 0
            return {
                "total": usage.total, "used": usage.used, "free": usage.free, "percent": round(percent, 1)
            }
        except Exception:
            return {"total": 1, "used": 0, "free": 0, "percent": 0}

    def _get_latest_files(self):
        """Finds latest tuning log and filtered list using scandir for speed"""
        latest_log = None
        latest_list = None
        max_log_mtime = 0
        max_list_mtime = 0

        try:
            if not os.path.exists(self.log_dir):
                return None, None

            for entry in os.scandir(self.log_dir):
                if not entry.is_file():
                    continue
                
                mtime = entry.stat().st_mtime
                if entry.name.startswith("Mover_tuning_") and entry.name.endswith(".log"):
                    if mtime > max_log_mtime:
                        max_log_mtime = mtime
                        latest_log = entry.path
                elif entry.name.startswith("Filtered_files_") and entry.name.endswith(".list"):
                    if mtime > max_list_mtime:
                        max_list_mtime = mtime
                        latest_list = entry.path
            
            return latest_log, latest_list
        except Exception as e:
            logger.error(f"Error scanning log directory: {e}")
            return None, None

    def get_latest_stats(self):
        try:
            latest_log, latest_list = self._get_latest_files()
            
            if not latest_log or not latest_list:
                return None
            
            stats = {
                "filename": os.path.basename(latest_log),
                "is_run": os.path.getsize(latest_list) > 500,
                "excluded": 0,
                "moved": 0,
                "timestamp": os.path.getmtime(latest_log)
            }

            # Optimization: Only read the last 1000 lines if files are massive
            with open(latest_list, 'r') as f:
                for line in f:
                    if "|" in line:
                        parts = line.split("|")
                        if len(parts) >= 4:
                            status = parts[3].strip().lower()
                            if status == "skipped":
                                stats["excluded"] += 1
                            elif status == "yes":
                                stats["moved"] += 1
            return stats
        except Exception as e:
            logger.error(f"Failed to parse mover logs: {e}")
            return None

def get_mover_parser():
    return MoverLogParser()
