import os
import logging
import shutil
from app.core.config import get_user_settings

logger = logging.getLogger(__name__)

class MoverLogParser:
    def __init__(self, log_dir="/mover_logs"):
        self.log_dir = log_dir

    def _get_files_by_type(self):
        """Categorizes all log sets into True Runs and Idle Checks"""
        true_runs = []
        idle_checks = []
        
        if not os.path.exists(self.log_dir):
            return [], []

        # We group by timestamp (the part after 'Mover_tuning_')
        # Format: Mover_tuning_2026-02-16T110551.log
        for entry in os.scandir(self.log_dir):
            if entry.name.startswith("Filtered_files_") and entry.name.endswith(".list"):
                mtime = entry.stat().st_mtime
                is_true = entry.stat().st_size > 500
                timestamp_str = entry.name.replace("Filtered_files_", "").replace(".list", "")
                
                log_set = {
                    "timestamp": timestamp_str,
                    "mtime": mtime,
                    "list_path": entry.path,
                    "log_path": os.path.join(self.log_dir, f"Mover_tuning_{timestamp_str}.log")
                }
                
                if is_true:
                    true_runs.append(log_set)
                else:
                    idle_checks.append(log_set)
        
        return sorted(true_runs, key=lambda x: x['mtime'], reverse=True), \
               sorted(idle_checks, key=lambda x: x['mtime'], reverse=True)

    def cleanup_logs(self):
        """Keeps most recent True Run and last 2 Idle Checks"""
        true_runs, idle_checks = self._get_files_by_type()
        files_deleted = 0

        # Keep 1st True Run, delete the rest
        for old_true in true_runs[1:]:
            self._delete_log_set(old_true)
            files_deleted += 1

        # Keep first 2 Idle Checks, delete the rest
        for old_idle in idle_checks[2:]:
            self._delete_log_set(old_idle)
            files_deleted += 1
        
        if files_deleted > 0:
            logger.info(f"Log cleanup complete. Removed {files_deleted} old log sets.")

    def _delete_log_set(self, log_set):
        try:
            if os.path.exists(log_set['list_path']): os.remove(log_set['list_path'])
            if os.path.exists(log_set['log_path']): os.remove(log_set['log_path'])
            # Also try to clean up associated summary/action files if they exist
            for prefix in ["Mover_action_", "Summary_"]:
                p = os.path.join(self.log_dir, f"{prefix}{log_set['timestamp']}.list")
                if os.path.exists(p): os.remove(p)
                p_txt = p.replace(".list", ".txt")
                if os.path.exists(p_txt): os.remove(p_txt)
        except Exception as e:
            logger.error(f"Failed to delete log set {log_set['timestamp']}: {e}")

    def get_latest_stats(self):
        true_runs, idle_checks = self._get_files_by_type()
        # We prefer the latest True Run for stats, but fallback to Idle if no True exists
        latest = true_runs[0] if true_runs else (idle_checks[0] if idle_checks else None)
        
        if not latest: return None
        
        is_true = latest in true_runs
        stats = {
            "filename": os.path.basename(latest['log_path']),
            "type_label": "True-Mover Run" if is_true else "Idle-Mover Check",
            "is_run": is_true,
            "excluded": 0,
            "moved": 0,
            "timestamp": latest['mtime']
        }

        with open(latest['list_path'], 'r') as f:
            for line in f:
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 4:
                        status = parts[3].strip().lower()
                        if status == "skipped": stats["excluded"] += 1
                        elif status == "yes": stats["moved"] += 1
        return stats

    def get_cache_usage(self):
        try:
            settings = get_user_settings()
            usage = shutil.disk_usage(settings.exclusions.cache_mount_path or "/mnt/cache")
            percent = (usage.used / usage.total) * 100 if usage.total > 0 else 0
            return {"total": usage.total, "used": usage.used, "free": usage.free, "percent": round(percent, 1)}
        except: return {"total": 1, "used": 0, "free": 0, "percent": 0}

def get_mover_parser():
    return MoverLogParser()
