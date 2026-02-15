from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.services.operations import run_exclusion_builder, run_full_sync
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/run/exclusions", response_class=HTMLResponse)
async def run_exclusions_endpoint():
    result = await run_exclusion_builder()
    color = "green" if result["status"] == "success" else "red"
    return f'<div class="bg-{color}-100 border border-{color}-400 text-{color}-700 px-4 py-2 rounded mb-4">{result["message"]}</div>'

@router.post("/run/all", response_class=HTMLResponse)
async def run_all_endpoint():
    result = await run_full_sync()
    color = "green" if result["status"] == "success" else "red"
    return f'<div class="bg-{color}-100 border border-{color}-400 text-{color}-700 px-4 py-2 rounded mb-4">{result["message"]}</div>'
