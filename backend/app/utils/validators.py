from typing import Dict, Set
from fastapi import HTTPException

# Supported file formats by category
SUPPORTED_FORMATS: Dict[str, Set[str]] = {
    "document": {
        "pdf", "doc", "docx", "txt", "rtf", "odt", "xls", "xlsx", 
        "csv", "ppt", "pptx", "epub", "mobi", "azw", "html"
    },
    "image": {
        "jpg", "jpeg", "png", "webp", "tiff", "tif", "bmp", "heic", 
        "svg", "ico", "raw", "cr2", "nef", "arw", "gif"
    },
    "audio": {
        "mp3", "wav", "aac", "ogg", "flac", "m4a", "opus", "wma"
    },
    "video": {
        "mp4", "mkv", "avi", "mov", "flv", "wmv", "webm", "m4v", "mpeg"
    },
    "archive": {
        "zip", "rar", "7z", "tar", "gz", "gzip", "bz2"
    },
    "code": {
        "json", "xml", "yaml", "yml", "ipynb", "md", "markdown"
    },
    "design": {
        "psd", "ai", "dwg", "dxf"
    },
    "database": {
        "sql", "parquet", "avro"
    }
}

class FileValidator:
    """Validates file formats and conversion requests"""
    
    @staticmethod
    def get_format_category(file_format: str) -> str:
        """Get the category of a file format"""
        file_format = file_format.lower().strip()
        
        for category, formats in SUPPORTED_FORMATS.items():
            if file_format in formats:
                return category
        
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_format}"
        )
    
    @staticmethod
    def validate_conversion(source_format: str, target_format: str) -> str:
        """Validate if conversion is supported. Returns category."""
        source_format = source_format.lower().strip()
        target_format = target_format.lower().strip()
        
        # Get categories
        source_category = FileValidator.get_format_category(source_format)
        target_category = FileValidator.get_format_category(target_format)
        
        # Check if formats are the same
        if source_format == target_format:
            raise HTTPException(
                status_code=400,
                detail="Source and target formats are the same"
            )
        
        # Most conversions should be within the same category or to PDF/image
        # Cross-category conversions are allowed for some cases
        allowed_cross_category = [
            ("document", "image"),  # doc to image
            ("image", "document"),  # image to pdf
            ("video", "audio"),     # video to audio
            ("video", "image"),     # video to gif/frames
            ("audio", "document"),  # audio to text (STT)
            ("document", "audio"),  # text to audio (TTS)
        ]
        
        if source_category != target_category:
            if (source_category, target_category) not in allowed_cross_category:
                raise HTTPException(
                    status_code=400,
                    detail=f"Conversion from {source_category} to {target_category} is not supported"
                )
        
        return source_category
    
    @staticmethod
    def is_format_supported(file_format: str) -> bool:
        """Check if a file format is supported"""
        file_format = file_format.lower().strip()
        
        for formats in SUPPORTED_FORMATS.values():
            if file_format in formats:
                return True
        
        return False
    
    @staticmethod
    def get_all_supported_formats() -> Dict[str, Set[str]]:
        """Get all supported formats by category"""
        return SUPPORTED_FORMATS
