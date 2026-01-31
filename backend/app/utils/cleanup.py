import asyncio
import os
from datetime import datetime, timedelta
from app.utils.file_handler import FileHandler
from app.config import settings

async def cleanup_old_files_task():
    """Background task to cleanup old files periodically"""
    while True:
        try:
            # Cleanup uploads
            deleted_uploads = FileHandler.cleanup_old_files(
                settings.upload_dir,
                settings.file_retention_hours
            )
            
            # Cleanup outputs
            deleted_outputs = FileHandler.cleanup_old_files(
                settings.output_dir,
                settings.file_retention_hours
            )
            
            if deleted_uploads > 0 or deleted_outputs > 0:
                print(f"Cleaned up {deleted_uploads} upload files and {deleted_outputs} output files")
            
        except Exception as e:
            print(f"Error in cleanup task: {e}")
        
        # Run cleanup every hour
        await asyncio.sleep(3600)

def schedule_cleanup():
    """Schedule the cleanup task"""
    asyncio.create_task(cleanup_old_files_task())
