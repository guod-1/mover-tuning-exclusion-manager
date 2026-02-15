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
            
            if not list_of_files:
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
                    line_low = line.lower().strip()
                    
                    # Skip empty lines or standard log headers
                    if not line_low or line_low.startswith('---'):
                        continue

                    # MOVER TUNING EXCLUSION PHRASES
                    # "Filtered" logs often just list the files they are ignoring.
                    # We check for common skipping keywords or lines starting with /mnt/
                    if any(x in line_low for x in ["skipping", "not moving", "ignoring", "exclusion"]):
                        stats["excluded"] += 1
                    elif line_low.startswith("/mnt/") and "skipping" in line_low:
                        stats["excluded"] += 1
                    # If it's a Filtered_fles_ log, almost every path listed is an exclusion
                    elif "filtered_fles_" in stats["filename"].lower() and line_low.startswith("/mnt/"):
                        stats["excluded"] += 1
                    
                    # MOVED LOGIC
                    elif "moving" in line_low and "skipping" not in line_low:
                        stats["moved"] += 1
                    
                    # ERROR LOGIC
                    elif "error" in line_low or "failed" in line_low:
                        stats["errors"] += 1
            
            logger.info(f"Parsed {stats['filename']}: Found {stats['excluded']} exclusions.")
            return stats
        except Exception as e:
            logger.error(f"Failed to parse mover logs: {e}")
            return None

def get_mover_parser():
    return MoverLogParser()
