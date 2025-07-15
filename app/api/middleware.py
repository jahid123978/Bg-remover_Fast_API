import logging
from datetime import datetime
from fastapi import HTTPException
from fastapi.applications import FastAPI

from app.models.exceptions import APIException
from app.models.schemas import ErrorResponse
from app.utils.responses import SafeJSONResponse

logger = logging.getLogger(__name__)

def setup_exception_handlers(app: FastAPI):
    """Setup exception handlers for the application."""
    
    @app.exception_handler(APIException)
    async def api_exception_handler(request, exc: APIException):
        """Handle custom API exceptions."""
        try:
            error_response = ErrorResponse.create_error(
                error=exc.message,
                error_code=exc.error_code,
                details={
                    "path": str(request.url.path),
                    "method": request.method,
                    "status_code": exc.status_code
                }
            )
            
            logger.warning(f"API Exception [{exc.error_code}]: {exc.message}")
            
            return SafeJSONResponse(
                status_code=exc.status_code,
                content=error_response.dict()
            )
            
        except Exception as handler_error:
            logger.error(f"Error in API exception handler: {handler_error}")
            return SafeJSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "error": exc.message,
                    "error_code": exc.error_code,
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException):
        """Handle FastAPI HTTP exceptions."""
        try:
            error_message = str(exc.detail) if exc.detail else "HTTP error occurred"
            
            error_response = ErrorResponse.create_error(
                error=error_message,
                error_code="HTTP_ERROR",
                details={
                    "path": str(request.url.path),
                    "method": request.method,
                    "status_code": exc.status_code
                }
            )
            
            logger.info(f"HTTP Exception [{exc.status_code}]: {error_message}")
            
            return SafeJSONResponse(
                status_code=exc.status_code,
                content=error_response.dict()
            )
            
        except Exception as handler_error:
            logger.error(f"Error in HTTP exception handler: {handler_error}")
            return SafeJSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "error": str(exc.detail),
                    "error_code": "HTTP_ERROR",
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        """Handle all other unexpected exceptions."""
        try:
            logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
            
            error_response = ErrorResponse.create_error(
                error="Internal server error",
                error_code="INTERNAL_ERROR",
                details={
                    "path": str(request.url.path),
                    "method": request.method,
                    "exception_type": type(exc).__name__
                }
            )
            
            return SafeJSONResponse(
                status_code=500,
                content=error_response.dict()
            )
            
        except Exception as handler_error:
            logger.error(f"Critical error in exception handler: {handler_error}")
            return SafeJSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Critical internal server error",
                    "error_code": "CRITICAL_ERROR",
                    "timestamp": datetime.now().isoformat()
                }
            )
