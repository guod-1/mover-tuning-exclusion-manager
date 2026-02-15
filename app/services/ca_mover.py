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
            # Find the most recent log file in the directory
            list_of_files = glob.glob(f'{self.log_dir}/*.log')
            if not list_of_files:
                return None

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
                    # Mover Tuning specific strings
                    if "skipping" in line.lower() or "not moving" in line.lower():
                        stats["excluded"] += 1
                    elif "moving" in line.lower() and "skipping" not in line.lower():
                        stats["moved"] += 1
                    elif "error" in line.lower():
                        stats["errors"] += 1
            
            return stats
        except Exception as e:
            logger.error(f"Failed to parse mover logs: {e}")
            return None

def get_mover_parser():
    return MoverLogParser()
