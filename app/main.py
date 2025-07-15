from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
import sys

from app.config.settings import settings
from app.core.model_manager import model_manager
from app.api.endpoints import auth, health, background, metrics
from app.models.exceptions import APIException
from app.utils.responses import SafeJSONResponse
from app.api.middleware import setup_exception_handlers

# Logging configuration
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    logger.info("Starting application...")
    await model_manager.load_model()
    logger.info("Application started successfully")
    
    yield
    
    logger.info("Shutting down application...")
    model_manager.unload_model()
    logger.info("Application shut down successfully")

# FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(background.router, prefix="/api", tags=["Background Removal"])
app.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        workers=1,
        log_level=settings.LOG_LEVEL.lower()
    )
