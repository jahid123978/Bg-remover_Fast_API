import time
from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.core.model_manager import model_manager
from app.config.settings import settings

router = APIRouter()

@router.get("/")
async def get_metrics(current_user: dict = Depends(get_current_user)):
    """Get API metrics."""
    return {
        "model_loaded": model_manager.is_loaded,
        "device": settings.DEVICE,
        "model_name": settings.MODEL_NAME,
        "uptime": time.time()
    }
