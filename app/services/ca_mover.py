import os
import glob
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class MoverLogParser:
    def __init__(self, log_dir="/mover_logs"):
        self.log_dir = log_dir

    def get_latest_stats(self):
        try:
            # 1. Prioritize files starting with "Filtered_fles_"
            list_of_files = glob.glob(f'{self.log_dir}/Filtered_fles_*.log')
            
            # 2. Fallback to any .log if the specific filter log doesn't exist
            if not list_of_files:
                list_of_files = glob.glob(f'{self.log_dir}/*.log')
                
            if not list_of_files:
                return None

            # Get the most recent one among the candidates
            latest_file = max(list_of_files, key=os.path.getctime)
            
            stats = {
                "filename": os.path.basename(latest_file),
                "excluded": 0,
                "moved": 0,
                "errors": 0,
                "timestamp": os.path.getmtime(latest_file)
            }

            with open(latest_file, 'r') as f:
                for line in f:
                    line_low = line.lower()
                    # Mover Tuning Log Logic
                    if "skipping" in line_low or "not moving" in line_low:
                        stats["excluded"] += 1
                    elif "moving" in line_low and "skipping" not in line_low:
                        stats["moved"] += 1
                    elif "error" in line_low:
                        stats["errors"] += 1
            
            logger.info(f"Parsed stats from {stats['filename']}: {stats['excluded']} excluded")
            return stats
        except Exception as e:
            logger.error(f"Failed to parse mover logs: {e}")
            return None

def get_mover_parser():
    return MoverLogParser()
