import io
import time
import logging
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import StreamingResponse
from PIL import Image

from app.models.schemas import ProcessingResponse, ImageFormat
from app.core.auth import get_current_user
from app.core.rate_limiter import rate_limiter
from app.core.model_manager import model_manager
from app.services.file_validator import FileValidator
from app.models.exceptions import ValidationException, ProcessingException, APIException

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/remove-background", response_model=ProcessingResponse)
async def remove_background(
    file: UploadFile = File(...),
    output_format: ImageFormat = ImageFormat.PNG,
    current_user: dict = Depends(get_current_user)
):
    """Remove background from uploaded image."""
    start_time = time.time()
    
    user_id = current_user.get("sub", "anonymous")
    if not await rate_limiter.check_rate_limit(user_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    
    try:
        FileValidator.validate_image_file(file)
        image_data = await file.read()
        image = await FileValidator.validate_image_content(image_data)
        
        original_size = image.size
        logger.info(f"Processing image with size: {original_size}")
        
        processed_image = await model_manager.process_image(image)
        
        output_buffer = io.BytesIO()
        
        if output_format == ImageFormat.JPEG:
            bg = Image.new("RGB", processed_image.size, (255, 255, 255))
            bg.paste(processed_image, mask=processed_image.split()[-1])
            processed_image = bg
        
        processed_image.save(output_buffer, format=output_format.value.upper())
        output_buffer.seek(0)
        
        processing_time = time.time() - start_time
        file_size = output_buffer.getbuffer().nbytes
        
        return StreamingResponse(
            io.BytesIO(output_buffer.getvalue()),
            media_type=f"image/{output_format.value}",
            headers={
                "Content-Disposition": f"attachment; filename=processed_{file.filename}",
                "X-Processing-Time": str(processing_time),
                "X-Original-Size": f"{original_size[0]}x{original_size[1]}",
                "X-File-Size": str(file_size)
            }
        )
        
    except ValidationException as e:
        logger.error(f"Validation error: {str(e)}")
        raise APIException(
            message=str(e),
            status_code=400,
            error_code="VALIDATION_ERROR"
        )
    except ProcessingException as e:
        logger.error(f"Processing error: {str(e)}")
        raise APIException(
            message=str(e),
            status_code=500,
            error_code="PROCESSING_ERROR"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise APIException(
            message="Internal server error",
            status_code=500,
            error_code="INTERNAL_ERROR"
        )