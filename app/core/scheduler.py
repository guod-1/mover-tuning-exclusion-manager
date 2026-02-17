from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.core.config import get_user_settings, save_user_settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def run_sync_task():
    from app.services.exclusions import get_exclusion_manager
    get_exclusion_manager().build_exclusions()
    
    # Save timestamp
    settings = get_user_settings()
    settings.exclusions.last_build = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_user_settings(settings)
    logger.info(f"Cron Task: Builder complete at {settings.exclusions.last_build}")

def run_stats_task():
    from app.services.ca_mover import get_mover_parser
    parser = get_mover_parser()
    parser.get_latest_stats()
    
    # Save timestamp
    settings = get_user_settings()
    settings.exclusions.last_stats_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_user_settings(settings)
    logger.info(f"Cron Task: Stats refresh complete at {settings.exclusions.last_stats_update}")

class CacheScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.sync_id = "full_sync"
        self.monitor_id = "log_monitor"

    def start(self):
        settings = get_user_settings()
        self.scheduler.add_job(run_sync_task, CronTrigger.from_crontab(settings.exclusions.full_sync_cron), id=self.sync_id)
        self.scheduler.add_job(run_stats_task, CronTrigger.from_crontab(settings.exclusions.log_monitor_cron), id=self.monitor_id)
        self.scheduler.start()

    def reload_jobs(self):
        settings = get_user_settings()
        self.scheduler.reschedule_job(self.sync_id, trigger=CronTrigger.from_crontab(settings.exclusions.full_sync_cron))
        self.scheduler.reschedule_job(self.monitor_id, trigger=CronTrigger.from_crontab(settings.exclusions.log_monitor_cron))

scheduler_service = CacheScheduler()
