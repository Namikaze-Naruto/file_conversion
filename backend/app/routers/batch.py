from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db, Conversion
from app.utils.file_handler import FileHandler
from app.utils.validators import FileValidator
from app.models import ConversionResponse
from datetime import datetime
import zipfile
import os
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/batch", tags=["batch"])

@router.post("/upload")
async def batch_upload(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload multiple files for batch conversion.
    
    Returns list of conversion IDs for each uploaded file.
    """
    
    if len(files) > 20:
        raise HTTPException(
            status_code=400, 
            detail="Maximum 20 files allowed per batch"
        )
    
    results = []
    
    for file in files:
        try:
            # Validate file
            FileValidator.validate_file(file)
            
            # Save file
            saved_path, file_format = await FileHandler.save_upload(file)
            
            # Create conversion record
            conversion = Conversion(
                source_format=file_format,
                original_filename=file.filename,
                input_path=saved_path,
                status="uploaded",
                uploaded_at=datetime.utcnow()
            )
            
            db.add(conversion)
            db.commit()
            db.refresh(conversion)
            
            results.append({
                "id": conversion.id,
                "filename": file.filename,
                "format": file_format,
                "status": "uploaded"
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "total": len(files),
        "successful": len([r for r in results if r.get("status") == "uploaded"]),
        "failed": len([r for r in results if r.get("status") == "error"]),
        "files": results
    }

@router.post("/convert")
async def batch_convert(
    conversion_ids: List[int],
    target_format: str,
    db: Session = Depends(get_db)
):
    """
    Convert multiple files to the same target format.
    
    This endpoint triggers conversions but returns immediately.
    Use /batch/status to check progress.
    """
    
    if len(conversion_ids) > 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum 20 conversions per batch"
        )
    
    results = []
    
    for conv_id in conversion_ids:
        conversion = db.query(Conversion).filter(Conversion.id == conv_id).first()
        
        if not conversion:
            results.append({
                "id": conv_id,
                "status": "error",
                "error": "Conversion not found"
            })
            continue
        
        # Update target format
        conversion.target_format = target_format
        conversion.status = "queued"
        db.commit()
        
        results.append({
            "id": conv_id,
            "filename": conversion.original_filename,
            "status": "queued",
            "source_format": conversion.source_format,
            "target_format": target_format
        })
    
    return {
        "total": len(conversion_ids),
        "queued": len([r for r in results if r.get("status") == "queued"]),
        "results": results,
        "message": "Batch conversion queued. Use /batch/status to check progress."
    }

@router.get("/status")
async def batch_status(
    conversion_ids: List[int],
    db: Session = Depends(get_db)
):
    """
    Check status of multiple conversions.
    """
    
    results = []
    
    for conv_id in conversion_ids:
        conversion = db.query(Conversion).filter(Conversion.id == conv_id).first()
        
        if not conversion:
            results.append({
                "id": conv_id,
                "status": "not_found"
            })
            continue
        
        results.append({
            "id": conversion.id,
            "filename": conversion.original_filename,
            "status": conversion.status,
            "source_format": conversion.source_format,
            "target_format": conversion.target_format,
            "error": conversion.error_message
        })
    
    completed = len([r for r in results if r.get("status") == "completed"])
    processing = len([r for r in results if r.get("status") == "processing"])
    failed = len([r for r in results if r.get("status") == "failed"])
    
    return {
        "total": len(conversion_ids),
        "completed": completed,
        "processing": processing,
        "failed": failed,
        "all_complete": completed == len(conversion_ids),
        "results": results
    }

@router.post("/download-zip")
async def download_batch_as_zip(
    conversion_ids: List[int],
    db: Session = Depends(get_db)
):
    """
    Download all converted files as a ZIP archive.
    """
    
    # Get all conversions
    conversions = db.query(Conversion).filter(
        Conversion.id.in_(conversion_ids),
        Conversion.status == "completed"
    ).all()
    
    if not conversions:
        raise HTTPException(
            status_code=404,
            detail="No completed conversions found"
        )
    
    # Create ZIP file
    zip_filename = f"batch_conversion_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.zip"
    zip_path = os.path.join(FileHandler.get_output_dir(), zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for conversion in conversions:
            if conversion.output_path and os.path.exists(conversion.output_path):
                # Add file to ZIP with original name
                base_name = os.path.splitext(conversion.original_filename)[0]
                output_filename = f"{base_name}.{conversion.target_format}"
                zipf.write(conversion.output_path, output_filename)
    
    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=zip_filename,
        headers={
            "Content-Disposition": f"attachment; filename={zip_filename}"
        }
    )
