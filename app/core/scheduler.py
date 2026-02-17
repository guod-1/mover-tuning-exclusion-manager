from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from app.core.config import get_user_settings
import logging

logger = logging.getLogger(__name__)

def run_sync_task():
    """Initializes the manager and rebuilds the exclusion file"""
    try:
        from app.services.exclusions import get_exclusion_manager
        manager = get_exclusion_manager()
        manager.build_exclusions()
        logger.info("Scheduled Task: build_exclusions completed successfully.")
    except Exception as e:
        logger.error(f"Scheduled Task Error (Sync): {str(e)}")

def run_stats_task():
    """Initializes the mover parser and refreshes the dashboard data"""
    try:
        from app.services.ca_mover import get_mover_parser
        parser = get_mover_parser()
        # Triggering get_latest_stats refreshes the internal cache of the parser
        stats = parser.get_latest_stats()
        logger.info(f"Scheduled Task: Log Monitor refreshed ({stats.get('excluded', 0)} protected).")
    except Exception as e:
        logger.error(f"Scheduled Task Error (Stats): {str(e)}")

class CacheScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.full_sync_job_id = "full_sync_job"
        self.log_monitor_job_id = "log_monitor_job"

    def start(self):
        settings = get_user_settings()
        
        cron_val = settings.exclusions.full_sync_cron or "0 * * * *"
        interval_val = int(settings.exclusions.log_monitor_interval or 300)

        # 1. Schedule Full Sync (Cron)
        self.scheduler.add_job(
            run_sync_task,
            CronTrigger.from_crontab(cron_val),
            id=self.full_sync_job_id,
            replace_existing=True
        )
        
        # 2. Schedule Log Monitor (Interval)
        self.scheduler.add_job(
            run_stats_task,
            IntervalTrigger(seconds=interval_val),
            id=self.log_monitor_job_id,
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info(f"Scheduler started: Full Sync ({cron_val}), Log Monitor ({interval_val}s)")

    def reload_jobs(self):
        settings = get_user_settings()
        cron_val = settings.exclusions.full_sync_cron or "0 * * * *"
        interval_val = int(settings.exclusions.log_monitor_interval or 300)

        self.scheduler.reschedule_job(
            self.full_sync_job_id, 
            trigger=CronTrigger.from_crontab(cron_val)
        )
        self.scheduler.reschedule_job(
            self.log_monitor_job_id, 
            trigger=IntervalTrigger(seconds=interval_val)
        )
        logger.info(f"Scheduler reloaded: Sync ({cron_val}), Monitor ({interval_val}s)")

    def shutdown(self):
        self.scheduler.shutdown()

scheduler_service = CacheScheduler()
