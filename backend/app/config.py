from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Application Settings
    app_name: str = "File Conversion Platform"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # File Settings
    max_file_size_mb: int = 50
    upload_dir: str = "uploads"
    output_dir: str = "outputs"
    file_retention_hours: int = 1
    
    # Rate Limiting
    rate_limit_per_minute: int = 10
    
    # CORS Settings
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # Database
    database_url: str = "sqlite:///./conversions.db"
    
    # External Tools
    ffmpeg_path: str = "ffmpeg"
    tesseract_path: str = "tesseract"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

settings = Settings()

# Ensure directories exist
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.output_dir, exist_ok=True)
