import logging
from fastapi import APIRouter
from app.models.schemas import HealthResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        model_status = True
        
        return HealthResponse.create_healthy_response(
            model_loaded=model_status,
            uptime="Service running normally"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse.create_unhealthy_response(
            reason=f"Health check failed: {str(e)}"
        )
