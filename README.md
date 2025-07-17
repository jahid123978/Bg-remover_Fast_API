# Background Removal API

A FastAPI-based service for removing backgrounds from images using JWT authentication.

## Features

- JWT-based authentication system
- Background removal from images
- Support for multiple output formats (PNG, JPG, etc.)
- Health check endpoint
- Metrics endpoint for monitoring
- Secure API key authentication

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python 3.8 or higher
- pip (Python package installer)
- curl (for testing API endpoints)

## Installation

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd background-removal-api
```
### Step 2: Add model_manager file (app/core/model_manager.py)
```vscode
import torch
import logging
import os
from transformers.models.auto.modeling_auto import AutoModelForImageSegmentation
from transformers.models.auto.processing_auto import AutoProcessor
from PIL import Image
import numpy as np
from huggingface_hub import login
from scipy import ndimage

from app.config.settings import settings
from app.models.exceptions import ProcessingException

logger = logging.getLogger(__name__)

class ModelManager:
    """Manages the RMBG-2.0 model lifecycle."""
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = settings.DEVICE
        self.is_loaded = False
        self.is_authenticated = False
    
    async def authenticate_huggingface(self):
        """Authenticate with Hugging Face using token."""
        try:
            hf_token = os.getenv("HF_TOKEN", "add_your_secret_token_Hugging_face")
            
            if not hf_token:
                raise ProcessingException("No Hugging Face token found")
            
            logger.info("Authenticating with Hugging Face...")
            login(token=hf_token)
            self.is_authenticated = True
            logger.info("Successfully authenticated with Hugging Face")
            
        except Exception as e:
            logger.error(f"Hugging Face authentication failed: {str(e)}")
            raise ProcessingException(f"Authentication failed: {str(e)}")
    
    async def load_model(self):
        """Load the RMBG-2.0 model."""
        try:
            if not self.is_authenticated:
                await self.authenticate_huggingface()
            
            logger.info(f"Loading RMBG-2.0 model on {self.device}")
            
            self.model = AutoModelForImageSegmentation.from_pretrained(
                settings.MODEL_NAME,
                torch_dtype=torch.float32,
                trust_remote_code=True
            )
            
            self.processor = AutoProcessor.from_pretrained(
                settings.MODEL_NAME,
                trust_remote_code=True
            )
            
            self.model.to(self.device)
            self.model.eval()
            
            self.is_loaded = True
            logger.info("Model loaded successfully")
            
        except Exception as e:
            self.is_authenticated = False
            logger.error(f"Failed to load model: {str(e)}")
            raise ProcessingException(f"Model loading failed: {str(e)}")
    
    async def process_image(self, image: Image.Image) -> Image.Image:
        """Process image to remove background."""
        if not self.is_loaded or self.processor is None:
            raise ProcessingException("Model or processor not loaded")
      
        try:
            inputs = self.processor(image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            if self.model is None:
                raise ProcessingException("Model is not loaded")
            
            with torch.no_grad():
                if 'images' in inputs:
                   outputs = self.model(inputs['images'])
                elif 'pixel_values' in inputs:
                   outputs = self.model(inputs['pixel_values'])
                else:
                  raise ValueError(f"Expected 'images' or 'pixel_values' in inputs")
            
            if hasattr(outputs, 'logits'):
                logits = outputs.logits
            elif isinstance(outputs, (list, tuple)):
                logits = outputs[0]
            else:
                logits = outputs
            
            if logits is None:
                raise ProcessingException("Could not extract logits from model output")
                
            if hasattr(logits, 'sigmoid'):
                mask = logits.sigmoid().cpu().numpy().squeeze()
            else:
                mask = np.array(logits).squeeze()
            
            if mask.min() < 0 or mask.max() > 1:
                mask = 1 / (1 + np.exp(-mask))
            
            mask = np.clip(mask, 0, 1)
            
            threshold = 0.5
            binary_mask = (mask > threshold).astype(np.uint8) * 255
            
            if binary_mask is None:
                raise ProcessingException("Could not get binary mask")
                
            binary_mask = ndimage.binary_fill_holes(binary_mask > 127)
            if binary_mask is None:
                raise ProcessingException("Could not get binary mask")
            binary_mask = binary_mask.astype(np.uint8) * 255
            binary_mask = ndimage.binary_opening(binary_mask > 127, iterations=1).astype(np.uint8) * 255
            
            mask_img = Image.fromarray(binary_mask, mode='L')
            mask_img = mask_img.resize(image.size, Image.Resampling.LANCZOS)
            
            result = Image.new("RGBA", image.size, (0, 0, 0, 0))
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            result.paste(image, mask=mask_img)
            
            return result
            
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            raise ProcessingException(f"Image processing failed: {str(e)}")
    
    def unload_model(self):
        """Unload the model and free resources."""
        if self.model is not None:
            del self.model
            del self.processor
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            self.is_loaded = False
            logger.info("Model unloaded successfully")
    
    def get_status(self):
        """Get model manager status."""
        return {
            "is_authenticated": self.is_authenticated,
            "is_loaded": self.is_loaded,
            "device": self.device,
            "model_name": settings.MODEL_NAME
        }

model_manager = ModelManager()
```

### Step 3: Create a Virtual Environment

Creating a virtual environment helps isolate your project dependencies from other Python projects on your system.

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
source venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
pip install kornia timm
```

### Step 4: Set Up Environment Variables

Create a `.env` file in your project root directory and configure the following variables:

```env
# API Configuration
API_SECRET_KEY=your-super-secret-key-change-in-production-abc123xyz789
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Server Configuration
HOST=localhost
PORT=8000
DEBUG=True
```

**Important Security Note:** The API key `your-super-secret-key-change-in-production-abc123xyz789` shown in your examples should be changed to a secure, randomly generated key in production environments.

### Step 5: Create Required Directories

The application expects certain directories to exist for input and output files:

```bash
mkdir -p app/images
mkdir -p app/outputs
```

### Step 6: Start the Application

```bash
# Run the FastAPI application
uvicorn app.main:app --reload
```

The `--reload` flag enables automatic reloading when you make code changes during development.

## API Endpoints

### Health Check
- **Endpoint:** `GET /health/`
- **Purpose:** Verify that the API is running correctly
- **Authentication:** Requires API key

### Authentication
- **Endpoint:** `POST /auth/token`
- **Purpose:** Generate JWT access token for API access
- **Parameters:** `user_id` (required)

### Background Removal
- **Endpoint:** `POST /api/remove-background`
- **Purpose:** Remove background from uploaded images
- **Authentication:** Requires JWT Bearer token
- **Parameters:** 
  - `file` (multipart/form-data): Image file to process
  - `output_format` (optional): Output format (PNG, JPG, etc.)

### Metrics
- **Endpoint:** `GET /metrics/`
- **Purpose:** Retrieve API usage metrics and statistics
- **Authentication:** Requires JWT Bearer token

## Testing the API

Follow these steps to test your API endpoints using the provided curl commands:

### Step 1: Test Health Check

This verifies that your API is running and accessible:

```bash
curl -X GET "http://localhost:8000/health/" \
  -H "Authorization: Bearer your-super-secret-key-change-in-production-abc123xyz789"
```

**Expected Response:** A JSON response indicating the API health status.

### Step 2: Generate Access Token

Before using protected endpoints, you need to obtain a JWT token:

```bash
curl -X POST "http://localhost:8000/auth/token" \
  -G -d "user_id=jahid12345"
```

**Expected Response:** A JSON object containing your access token.

**Example Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Step 3: Test Background Removal

Place a test image in the `app/images/` directory (e.g., `profile3.jpg`) and run:

```bash
curl -X POST "http://localhost:8000/api/remove-background" \
     -H "Authorization: Bearer Your Access Token" \
     -F "file=@./app/images/profile7.jpg" \
     -F "output_format=PNG" \
     --output "app/outputs/processed_portrait4.png"
```

**Important:** Replace `YOUR_ACCESS_TOKEN_HERE` with the actual token you received from Step 2.

**Expected Result:** A processed image with the background removed will be saved to `app/outputs/processed_portrait1.png`.

### Step 4: Check Metrics

Monitor your API usage and performance:

```bash
curl -X GET "http://localhost:8000/metrics/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

**Expected Response:** JSON data containing API usage statistics and metrics.

## Understanding the Authentication Flow

The API uses a two-tier authentication system for enhanced security:

1. **API Key Authentication:** Used for initial health checks and token generation
2. **JWT Authentication:** Used for accessing protected endpoints like background removal and metrics

This approach allows you to control access at multiple levels and provides flexibility in managing different types of clients.

## Troubleshooting

### Common Issues and Solutions

**Issue:** "Connection refused" error
**Solution:** Ensure the API server is running on the correct port (8000) and that no firewall is blocking the connection.

**Issue:** "Unauthorized" error
**Solution:** Verify that your API key or JWT token is correct and hasn't expired. JWT tokens have a limited lifespan for security purposes.

**Issue:** "File not found" error
**Solution:** Check that the image file exists in the specified path and that the application has read permissions.

**Issue:** "Invalid token" error
**Solution:** Generate a new JWT token using the `/auth/token` endpoint, as tokens expire after a certain period.

