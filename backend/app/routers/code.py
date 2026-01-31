from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.database import get_db, Conversion
from app.services.code_converter import CodeConverter
from app.models import ConversionResponse
import os
from datetime import datetime

router = APIRouter(prefix="/api/code", tags=["code"])

@router.post("/convert/{conversion_id}", response_model=ConversionResponse)
async def convert_code(
    conversion_id: int,
    target_format: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Convert code and data formats.
    
    Supported conversions:
    - JSON ↔ CSV, XML, YAML
    - CSV ↔ XML, JSON
    - Excel → JSON
    - HTML → PDF, Markdown
    - Markdown → HTML
    - Jupyter Notebook → HTML, PDF
    """
    conversion = db.query(Conversion).filter(Conversion.id == conversion_id).first()
    
    if not conversion:
        raise HTTPException(status_code=404, detail="Conversion not found")
    
    try:
        conversion.status = "processing"
        db.commit()
        
        # Build input path from filename
        from app.config import settings
        input_path = os.path.join(settings.upload_dir, conversion.filename)
        
        if not os.path.exists(input_path):
            raise HTTPException(status_code=404, detail="Input file not found")
        
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_filename = f"{base_name}_converted.{target_format.lower()}"
        output_path = os.path.join(settings.output_dir, output_filename)
        
        result_path = await CodeConverter.convert(
            input_path=input_path,
            output_path=output_path,
            source_format=conversion.source_format,
            target_format=target_format
        )
        
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
        
    except NotImplementedError as e:
        conversion.status = "failed"
        conversion.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        conversion.status = "failed"
        conversion.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Code conversion failed: {str(e)}")
