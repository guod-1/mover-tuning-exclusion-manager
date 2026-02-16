import os
import glob
import logging
import datetime

logger = logging.getLogger(__name__)

class MoverLogParser:
    def __init__(self, log_dir="/mover_logs"):
        self.log_dir = log_dir

    def get_latest_stats(self):
        """Compatibility wrapper for dashboard"""
        return self.get_stats_for_file()

    def get_stats_for_file(self, filename=None):
        try:
            list_of_files = glob.glob(f'{self.log_dir}/Filtered_files_*.list')
            if not list_of_files:
                list_of_files = glob.glob(f'{self.log_dir}/*.log')
            if not list_of_files: return None
            
            # Sort by time to get the most recent log
            latest_file = max(list_of_files, key=os.path.getctime)
            
            # Find the most recent log that ACTUALLY moved or skipped files (a 'Run')
            run_file = None
            for f in sorted(list_of_files, key=os.path.getctime, reverse=True):
                if os.path.getsize(f) > 500: # Threshold: tiny logs are usually just 'checks'
                    run_file = f
                    break
            
            target_file = filename if filename else latest_file
            stats = {
                "filename": os.path.basename(target_file),
                "is_run": os.path.getsize(target_file) > 500,
                "excluded": 0,
                "moved": 0,
                "total_bytes_kept": 0,
                "timestamp": os.path.getmtime(target_file),
                "last_run_timestamp": os.path.getmtime(run_file) if run_file else None,
                "efficiency": 0
            }

            with open(target_file, 'r') as f:
                for line in f:
                    if "|" in line:
                        parts = line.strip().split("|")
                        if len(parts) >= 11:
                            status = parts[3].lower()
                            size = int(parts[6]) if parts[6].isdigit() else 0
                            if status == "skipped":
                                stats["excluded"] += 1
                                stats["total_bytes_kept"] += size
                            elif status == "yes":
                                stats["moved"] += 1
            
            total = stats["excluded"] + stats["moved"]
            if total > 0:
                stats["efficiency"] = round((stats["excluded"] / total) * 100, 1)
            return stats
        except Exception as e:
            logger.error(f"Failed to parse mover logs: {e}")
            return None

def get_mover_parser():
    return MoverLogParser()
