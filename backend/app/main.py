from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime
import os

from app.config import settings
from app.database import get_db, Conversion, Base, engine
from app.models import ConversionResponse, ConversionStatus, ErrorResponse
from app.utils.file_handler import FileHandler
from app.utils.validators import FileValidator
from app.utils.cleanup import schedule_cleanup
from app.middleware.rate_limiter import RateLimitMiddleware
from app.routers import documents, images, audio, video, archives, code, design, database_conv, security, ai_powered, batch

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Comprehensive file conversion platform supporting 100+ conversion types",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins if not settings.debug else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(documents.router)
app.include_router(images.router)
app.include_router(audio.router)
app.include_router(video.router)
app.include_router(archives.router)
app.include_router(code.router)
app.include_router(design.router)
app.include_router(database_conv.router)
app.include_router(security.router)
app.include_router(ai_powered.router)
app.include_router(batch.router)

# Schedule cleanup task on startup
@app.on_event("startup")
async def startup_event():
    schedule_cleanup()
    print(f"[STARTED] {settings.app_name} v{settings.app_version}")
    print(f"Upload directory: {settings.upload_dir}")
    print(f"Output directory: {settings.output_dir}")
    print(f"Max file size: {settings.max_file_size_mb}MB")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "supported_formats": FileValidator.get_all_supported_formats()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/api/upload", response_model=ConversionResponse)
async def upload_file(
    file: UploadFile = File(...),
    target_format: str = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Upload a file for conversion
    
    - **file**: File to upload
    - **target_format**: Target format for conversion (optional, can be specified later)
    """
    try:
        # Save uploaded file
        file_path = await FileHandler.save_upload_file(file)
        
        # Validate file size
        FileHandler.validate_file_size(file_path)
        
        # Get file info
        source_format = FileHandler.get_file_extension(file.filename)
        file_size_mb = FileHandler.get_file_size_mb(file_path)
        
        # Validate source format
        if not FileValidator.is_format_supported(source_format):
            FileHandler.delete_file(file_path)
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported source format: {source_format}"
            )
        
        # Create conversion record
        conversion = Conversion(
            filename=os.path.basename(file_path),
            source_format=source_format,
            target_format=target_format or "",
            file_size=file_size_mb,
            status="uploaded",
            ip_address=request.client.host if request else None
        )
        db.add(conversion)
        db.commit()
        db.refresh(conversion)
        
        return conversion
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/conversions/{conversion_id}", response_model=ConversionResponse)
async def get_conversion(conversion_id: int, db: Session = Depends(get_db)):
    """Get conversion status and details"""
    conversion = db.query(Conversion).filter(Conversion.id == conversion_id).first()
    
    if not conversion:
        raise HTTPException(status_code=404, detail="Conversion not found")
    
    return conversion

@app.get("/api/conversions")
async def list_conversions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List recent conversions"""
    conversions = db.query(Conversion).order_by(
        Conversion.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return conversions

@app.get("/api/download/{conversion_id}")
async def download_file(conversion_id: int, db: Session = Depends(get_db)):
    """Download converted file"""
    conversion = db.query(Conversion).filter(Conversion.id == conversion_id).first()
    
    if not conversion:
        raise HTTPException(status_code=404, detail="Conversion not found")
    
    if conversion.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Conversion is not ready. Status: {conversion.status}"
        )
    
    # Build output file path
    output_filename = FileHandler.get_output_filename(
        conversion.filename,
        conversion.target_format
    )
    output_path = os.path.join(settings.output_dir, output_filename)
    
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Converted file not found")
    
    return FileResponse(
        output_path,
        media_type="application/octet-stream",
        filename=output_filename
    )

@app.get("/api/formats")
async def get_supported_formats():
    """Get all supported file formats"""
    return FileValidator.get_all_supported_formats()

@app.delete("/api/conversions/{conversion_id}")
async def delete_conversion(conversion_id: int, db: Session = Depends(get_db)):
    """Delete a conversion and its files"""
    conversion = db.query(Conversion).filter(Conversion.id == conversion_id).first()
    
    if not conversion:
        raise HTTPException(status_code=404, detail="Conversion not found")
    
    # Delete files
    input_path = os.path.join(settings.upload_dir, conversion.filename)
    FileHandler.delete_file(input_path)
    
    if conversion.target_format:
        output_filename = FileHandler.get_output_filename(
            conversion.filename,
            conversion.target_format
        )
        output_path = os.path.join(settings.output_dir, output_filename)
        FileHandler.delete_file(output_path)
    
    # Delete database record
    db.delete(conversion)
    db.commit()
    
    return {"message": "Conversion deleted successfully"}

# Mount static files for frontend
import os
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend")
if os.path.exists(frontend_path):
    try:
        app.mount("/static", StaticFiles(directory=frontend_path, html=True), name="static")
        print(f"Frontend mounted at /static from {frontend_path}")
    except Exception as e:
        print(f"Warning: Could not mount static files: {e}")
else:
    print(f"Warning: Frontend directory not found at {frontend_path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
