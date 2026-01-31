import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
from app.config import settings

class FileHandler:
    """Handles file upload, storage, and cleanup operations"""
    
    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        """Generate a unique filename preserving the original extension"""
        name, ext = os.path.splitext(original_filename)
        unique_id = uuid.uuid4().hex[:8]
        return f"{name}_{unique_id}{ext}"
    
    @staticmethod
    async def save_upload_file(upload_file: UploadFile, directory: str = None) -> str:
        """Save uploaded file to disk and return the file path"""
        if directory is None:
            directory = settings.upload_dir
        
        # Generate unique filename
        filename = FileHandler.generate_unique_filename(upload_file.filename)
        file_path = os.path.join(directory, filename)
        
        # Ensure directory exists
        os.makedirs(directory, exist_ok=True)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        return file_path
    
    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """Get file size in MB"""
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension without the dot"""
        return os.path.splitext(filename)[1].lstrip('.').lower()
    
    @staticmethod
    def validate_file_size(file_path: str) -> None:
        """Validate file size doesn't exceed the limit"""
        size_mb = FileHandler.get_file_size_mb(file_path)
        if size_mb > settings.max_file_size_mb:
            raise HTTPException(
                status_code=413,
                detail=f"File size ({size_mb:.2f}MB) exceeds maximum allowed size ({settings.max_file_size_mb}MB)"
            )
    
    @staticmethod
    def delete_file(file_path: str) -> None:
        """Delete a file if it exists"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
    
    @staticmethod
    def cleanup_old_files(directory: str, hours: int) -> int:
        """Delete files older than specified hours. Returns count of deleted files."""
        import time
        
        deleted_count = 0
        current_time = time.time()
        cutoff_time = current_time - (hours * 3600)
        
        if not os.path.exists(directory):
            return 0
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_modified_time = os.path.getmtime(file_path)
                if file_modified_time < cutoff_time:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except Exception as e:
                        print(f"Error deleting old file {file_path}: {e}")
        
        return deleted_count
    
    @staticmethod
    def get_output_filename(input_filename: str, target_format: str) -> str:
        """Generate output filename with new extension"""
        name = os.path.splitext(input_filename)[0]
        return f"{name}.{target_format.lower()}"
