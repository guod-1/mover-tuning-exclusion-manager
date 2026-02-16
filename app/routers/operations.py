from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.services.operations import run_exclusion_builder, run_full_sync

router = APIRouter()

@router.post("/run/exclusions", response_class=HTMLResponse)
async def trigger_exclusion_build():
    result = run_exclusion_builder()
    if result.get("success"):
        return f"""
        <div class="bg-green-900/30 border border-green-800 text-green-200 px-4 py-3 rounded-lg flex items-center justify-between animate-fade-in-down mb-4">
            <div class="flex items-center">
                <i class="fa-solid fa-check-circle mr-3 text-green-400"></i>
                <span>Exclusion list rebuilt successfully! ({result.get('total', 0)} items)</span>
            </div>
            <button onclick="this.parentElement.remove()" class="text-green-400 hover:text-white"><i class="fa-solid fa-times"></i></button>
        </div>
        """
    else:
        return f"""
        <div class="bg-red-900/30 border border-red-800 text-red-200 px-4 py-3 rounded-lg flex items-center justify-between animate-fade-in-down mb-4">
            <div class="flex items-center">
                <i class="fa-solid fa-exclamation-circle mr-3 text-red-400"></i>
                <span>Error: {result.get('message', 'Unknown error')}</span>
            </div>
            <button onclick="this.parentElement.remove()" class="text-red-400 hover:text-white"><i class="fa-solid fa-times"></i></button>
        </div>
        """

@router.post("/run/all", response_class=HTMLResponse)
async def trigger_full_sync():
    run_full_sync()
    return f"""
    <div class="bg-green-900/30 border border-green-800 text-green-200 px-4 py-3 rounded-lg flex items-center justify-between animate-fade-in-down mb-4">
        <div class="flex items-center">
            <i class="fa-solid fa-check-circle mr-3 text-green-400"></i>
            <span>Full sync completed successfully.</span>
        </div>
        <button onclick="this.parentElement.remove()" class="text-green-400 hover:text-white"><i class="fa-solid fa-times"></i></button>
    </div>
    """
