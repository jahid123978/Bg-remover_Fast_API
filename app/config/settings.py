import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application configuration settings with environment variable support."""
    
    # API Configuration
    API_TITLE: str = "Production Background Removal API"
    API_VERSION: str = "2.0.0"
    API_DESCRIPTION: str = "High-performance background removal API using RMBG-2.0 model"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "JahidHasanskjhgdkdjhskhgkgjhskf")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Upload Limits
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    
    # Model Configuration
    MODEL_NAME: str = "briaai/RMBG-2.0"
    DEVICE: str = "cuda" if os.getenv("CUDA_AVAILABLE", "false").lower() == "true" else "cpu"
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "https://yourdomain.com"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Hugging Face
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")

settings = Settings()
