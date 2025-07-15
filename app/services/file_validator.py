import io
from pathlib import Path
from fastapi import UploadFile
from PIL import Image

from app.config.settings import settings
from app.models.exceptions import ValidationException

class FileValidator:
    """Handles file validation with security checks."""
    
    @staticmethod
    def validate_image_file(file: UploadFile) -> None:
        """Comprehensive image file validation."""
        if file.size is None:
            raise ValidationException("file is empty")
        if file.size > settings.MAX_FILE_SIZE:
            raise ValidationException(
                f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        if file.filename:
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in settings.ALLOWED_EXTENSIONS:
                raise ValidationException(
                    f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
                )
        
        allowed_mime_types = {
            "image/jpeg", "image/jpg", "image/png", 
            "image/webp", "image/bmp"
        }
        if file.content_type not in allowed_mime_types:
            raise ValidationException(f"Invalid MIME type: {file.content_type}")
    
    @staticmethod
    async def validate_image_content(image_data: bytes) -> Image.Image:
        """Validate image content and return PIL Image."""
        try:
            image = Image.open(io.BytesIO(image_data))
            image.verify()
            image = Image.open(io.BytesIO(image_data))
            return image
            
        except Exception as e:
            if isinstance(e, ValidationException):
                raise
            raise ValidationException(f"Invalid image format: {str(e)}")