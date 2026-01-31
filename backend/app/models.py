from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ConversionRequest(BaseModel):
    source_format: str = Field(..., description="Source file format")
    target_format: str = Field(..., description="Target file format")

class ConversionResponse(BaseModel):
    id: int
    filename: str
    source_format: str
    target_format: str
    file_size: float
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    download_url: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class ConversionStatus(BaseModel):
    id: int
    status: str
    progress: Optional[int] = None
    message: Optional[str] = None
    download_url: Optional[str] = None

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
