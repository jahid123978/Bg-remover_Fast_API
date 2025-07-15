from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Tuple
from enum import Enum
from datetime import datetime

class ImageFormat(str, Enum):
    """Supported image output formats."""
    PNG = "png"
    WEBP = "webp"
    JPEG = "jpeg"

class ProcessingResponse(BaseModel):
    """Response model for successful image processing."""
    success: bool = True
    message: str = "Background removed successfully"
    processing_time: float = Field(..., description="Processing time in seconds")
    original_size: Dict[str, int] = Field(..., description="Original image dimensions")
    output_format: ImageFormat = Field(..., description="Output image format")
    file_size: int = Field(..., description="Output file size in bytes")
    
    @classmethod
    def create_success_response(cls, processing_time: float, original_size: Tuple[int, int], 
                               output_format: ImageFormat, file_size: int, message: str = ""):
        """Factory method to create success response."""
        return cls(
            processing_time=processing_time,
            original_size={"width": original_size[0], "height": original_size[1]},
            output_format=output_format,
            file_size=file_size,
            message=message or "Background removed successfully"
        )

class ErrorResponse(BaseModel):
    """Standard error response model."""
    success: bool = False
    error: str = Field(..., description="Error description")
    error_code: str = Field(..., description="Error code for debugging")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    
    @classmethod
    def create_error(cls, error: str, error_code: str, details: Optional[Dict[str, Any]] = None):
        """Factory method to create error responses."""
        return cls(
            error=error,
            error_code=error_code,
            details=details
        )

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = "healthy"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    version: str = "2.0.0"
    model_loaded: bool = True
    uptime: Optional[str] = Field(default=None, description="Application uptime")
    
    @classmethod
    def create_healthy_response(cls, model_loaded: bool = True, uptime: Optional[str] = None):
        """Factory method to create healthy responses."""
        return cls(
            model_loaded=model_loaded,
            uptime=uptime
        )
    
    @classmethod
    def create_unhealthy_response(cls, reason: str = "Service unavailable"):
        """Factory method to create unhealthy responses."""
        return cls(
            status="unhealthy",
            model_loaded=False,
            uptime=None
        )
