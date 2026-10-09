from fastapi import APIRouter, BackgroundTasks
from backend.sync.scheduler import run_sync_cycle, get_sync_status

router = APIRouter(prefix="/sync", tags=["System Sync"])

@router.get("/status")
def sync_status():
    """Returns status and timestamps of the automated data synchronization engine."""
    return get_sync_status()

@router.post("/run")
async def trigger_sync(background_tasks: BackgroundTasks):
    """Triggers an immediate background synchronization cycle for stocks and IPOs."""
    background_tasks.add_task(run_sync_cycle)
    return {
        "status": "triggered",
        "message": "Data synchronization cycle started in background."
    }
