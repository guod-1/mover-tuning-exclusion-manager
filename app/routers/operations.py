from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.services.operations import run_exclusion_builder, run_full_sync
from app.services.exclusions import get_exclusion_manager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/run/exclusions", response_class=HTMLResponse)
async def run_exclusions_endpoint():
    # 1. Run the Logic
    result = await run_exclusion_builder()
    
    # 2. Fetch Fresh Stats
    manager = get_exclusion_manager()
    stats = manager.get_exclusion_stats()
    new_count = stats.get('total_count', 0)
    
    # 3. Determine Color
    color = "green" if result["status"] == "success" else "red"
    
    # 4. Return Response + OOB Swap for the Dashboard Counter
    # The second div with hx-swap-oob="true" will find the element with id="dashboard-exclusion-count" 
    # anywhere on the page and update it instantly.
    return f"""
    <div class="bg-{color}-100 border border-{color}-400 text-{color}-700 px-4 py-2 rounded mb-4 animate-pulse">
        {result["message"]}
    </div>
    <span id="dashboard-exclusion-count" hx-swap-oob="true" class="text-3xl font-bold text-gray-900 dark:text-white">
        {new_count}
    </span>
    """

@router.post("/run/all", response_class=HTMLResponse)
async def run_all_endpoint():
    # 1. Run the Logic
    result = await run_full_sync()
    
    # 2. Fetch Fresh Stats
    manager = get_exclusion_manager()
    stats = manager.get_exclusion_stats()
    new_count = stats.get('total_count', 0)
    
    # 3. Determine Color
    color = "green" if result["status"] == "success" else "red"
    
    # 4. Return Response + OOB Swap
    return f"""
    <div class="bg-{color}-100 border border-{color}-400 text-{color}-700 px-4 py-2 rounded mb-4 animate-pulse">
        {result["message"]}
    </div>
    <span id="dashboard-exclusion-count" hx-swap-oob="true" class="text-3xl font-bold text-gray-900 dark:text-white">
        {new_count}
    </span>
    """
