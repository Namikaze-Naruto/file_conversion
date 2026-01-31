from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.database import get_db, Conversion
from app.services.audio_converter import AudioConverter
from app.models import ConversionResponse
import os
from datetime import datetime

router = APIRouter(prefix="/api/audio", tags=["audio"])

@router.post("/convert/{conversion_id}", response_model=ConversionResponse)
async def convert_audio(
    conversion_id: int,
    target_format: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Convert audio files between formats or perform audio operations.
    
    Supported conversions:
    - MP3 ↔ WAV, AAC, OGG
    - FLAC → MP3
    - M4A → MP3
    - WAV → FLAC
    - OPUS → MP3
    - Text → Audio (TTS)
    - Video → Audio extraction
    """
    conversion = db.query(Conversion).filter(Conversion.id == conversion_id).first()
    
    if not conversion:
        raise HTTPException(status_code=404, detail="Conversion not found")
    
    if conversion.status == "completed":
        raise HTTPException(status_code=400, detail="Conversion already completed")
    
    try:
        conversion.status = "processing"
        db.commit()
        
        # Build input path from filename
        from app.config import settings
        input_path = os.path.join(settings.upload_dir, conversion.filename)
        source_format = conversion.source_format
        
        if not os.path.exists(input_path):
            raise HTTPException(status_code=404, detail="Input file not found")
        
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_filename = f"{base_name}_converted.{target_format.lower()}"
        output_dir = os.path.dirname(input_path).replace('uploads', 'outputs')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)
        
        result_path = await AudioConverter.convert(
            input_path=input_path,
            output_path=output_path,
            source_format=source_format,
            target_format=target_format
        )
        
        conversion.output_path = result_path
        conversion.target_format = target_format
        conversion.status = "completed"
        conversion.completed_at = datetime.utcnow()
        db.commit()
        
        return {
            "id": conversion.id,
            "filename": conversion.filename,
            "source_format": conversion.source_format,
            "target_format": conversion.target_format,
            "file_size": conversion.file_size,
            "status": "completed",
            "created_at": conversion.created_at,
            "completed_at": conversion.completed_at,
            "download_url": f"/api/download/{conversion.id}",
            "error_message": None
        }
        
    except Exception as e:
        conversion.status = "failed"
        conversion.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Audio conversion failed: {str(e)}")
