from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from app.services.exclusions import get_exclusion_manager

router = APIRouter()


@router.post("/run/exclusions")
async def trigger_exclusion_build():
    """Manually trigger exclusion builder"""
    try:
        excl = get_exclusion_manager()
        excl.build_exclusions()
        return RedirectResponse(url="/?success=exclusions_built", status_code=303)
    except Exception as e:
        return RedirectResponse(url="/?error=build_failed", status_code=303)


@router.post("/run/all")
async def trigger_full_sync():
    """Manually trigger full sync"""
    try:
        excl = get_exclusion_manager()
        excl.build_exclusions()
        return RedirectResponse(url="/?success=sync_complete", status_code=303)
    except Exception as e:
        return RedirectResponse(url="/?error=sync_failed", status_code=303)
