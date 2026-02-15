import datetime
import logging
from app.core.config import get_user_settings, save_user_settings
from app.services.radarr import get_radarr_client
from app.services.sonarr import get_sonarr_client
from app.services.exclusions import get_exclusion_manager

logger = logging.getLogger(__name__)

async def run_full_sync():
    logger.info("Starting manual full sync...")
    settings = get_user_settings()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Sync Radarr
    try:
        get_radarr_client().get_all_tags()
        settings.radarr.last_sync = now
    except Exception as e:
        logger.error(f"Radarr sync failed: {e}")

    # Sync Sonarr
    try:
        get_sonarr_client().get_all_tags()
        settings.sonarr.last_sync = now
    except Exception as e:
        logger.error(f"Sonarr sync failed: {e}")

    # Save sync times before running builder
    save_user_settings(settings)

    # Run the exclusion builder
    try:
        excl = get_exclusion_manager()
        count = excl.combine_exclusions()
        
        # Update build timestamp using the correct attribute name
        settings = get_user_settings()
        settings.exclusions.last_build = now
        save_user_settings(settings)
        
        logger.info(f"Full sync complete. Generated {count} exclusions.")
        return {"status": "success", "count": count}
    except Exception as e:
        logger.error(f"Exclusion builder failed during sync: {e}")
        return {"status": "error", "message": str(e)}
