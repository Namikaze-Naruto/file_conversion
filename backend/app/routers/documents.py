from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import os

from app.database import get_db, Conversion
from app.config import settings
from app.services.document_converter import DocumentConverter
from app.utils.file_handler import FileHandler

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("/convert/{conversion_id}")
async def convert_document(
    conversion_id: int,
    target_format: str,
    db: Session = Depends(get_db)
):
    """
    Convert a document to the specified target format
    
    - **conversion_id**: ID of the uploaded file
    - **target_format**: Target format (pdf, docx, txt, csv, xlsx, etc.)
    """
    # Get conversion record
    conversion = db.query(Conversion).filter(Conversion.id == conversion_id).first()
    
    if not conversion:
        raise HTTPException(status_code=404, detail="Conversion not found")
    
    if conversion.status == "completed":
        raise HTTPException(status_code=400, detail="Conversion already completed")
    
    # Update target format if not set
    if not conversion.target_format or conversion.target_format != target_format:
        conversion.target_format = target_format
        db.commit()
    
    try:
        # Update status to processing
        conversion.status = "processing"
        db.commit()
        
        # Build file paths
        input_path = os.path.join(settings.upload_dir, conversion.filename)
        output_filename = FileHandler.get_output_filename(conversion.filename, target_format)
        output_path = os.path.join(settings.output_dir, output_filename)
        
        # Check if input file exists
        if not os.path.exists(input_path):
            raise HTTPException(status_code=404, detail="Input file not found")
        
        # Perform conversion
        result_path = await DocumentConverter.convert(
            input_path,
            output_path,
            conversion.source_format,
            target_format
        )
        
        # Update conversion status
        conversion.status = "completed"
        conversion.completed_at = datetime.utcnow()
        conversion.error_message = None
        db.commit()
        
        return {
            "id": conversion.id,
            "status": "completed",
            "download_url": f"/api/download/{conversion.id}",
            "output_filename": output_filename
        }
        
    except NotImplementedError as e:
        conversion.status = "failed"
        conversion.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=501, detail=str(e))
        
    except Exception as e:
        conversion.status = "failed"
        conversion.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

@router.get("/supported-conversions")
async def get_supported_conversions():
    """Get list of supported document conversions"""
    return {
        "pdf": ["docx", "doc", "txt"],
        "docx": ["pdf", "txt"],
        "txt": ["pdf", "docx"],
        "xlsx": ["csv", "pdf"],
        "xls": ["csv", "pdf"],
        "csv": ["xlsx", "pdf"]
    }
