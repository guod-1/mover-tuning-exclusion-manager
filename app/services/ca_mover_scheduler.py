"""
CA Mover Log Checker

Scheduled task to check CA Mover logs daily
"""

import logging
from app.services.ca_mover import get_ca_mover_monitor

logger = logging.getLogger(__name__)


def check_ca_mover_logs():
    """Check CA Mover Tuning logs (runs daily at 11:30 PM)"""
    logger.info("Running scheduled CA Mover log check...")
    
    ca_monitor = get_ca_mover_monitor()
    ca_status = ca_monitor.parse_log()
    
    logger.info(f"CA Mover Status: {ca_status['status']}")
    logger.info(f"Files Excluded: {ca_status['files_excluded']}")
    logger.info(f"Files Moved: {ca_status.get('files_moved', 0)}")
    
    if ca_status['last_run']:
        logger.info(f"Last Run: {ca_status['last_run']}")
    
    return ca_status
