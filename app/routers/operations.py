from fastapi import APIRouter
from app.services.operations import run_exclusion_builder, run_full_sync

router = APIRouter()

@router.post("/run/exclusions")
async def trigger_exclusion_build():
    return run_exclusion_builder()

@router.post("/run/all")
async def trigger_full_sync():
    return run_full_sync()
