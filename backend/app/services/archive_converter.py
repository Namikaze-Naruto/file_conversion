import zipfile
import py7zr
import tarfile
import os
import shutil
from typing import Optional

try:
    import rarfile
    RARFILE_AVAILABLE = True
except ImportError:
    RARFILE_AVAILABLE = False

class ArchiveConverter:
    """Handles archive/compression format conversions"""
    
    @staticmethod
    async def convert(input_path: str, output_path: str, 
                     source_format: str, target_format: str) -> str:
        """Main conversion dispatcher"""
        
        source_format = source_format.lower().replace('.', '')
        target_format = target_format.lower().replace('.', '')
        
        # Extract to temp directory
        temp_dir = output_path + '_temp_extract'
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Extract source archive
            await ArchiveConverter.extract_archive(input_path, temp_dir, source_format)
            
            # Create target archive
            await ArchiveConverter.create_archive(temp_dir, output_path, target_format)
            
            return output_path
            
        finally:
            # Cleanup temp directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    @staticmethod
    async def extract_archive(archive_path: str, extract_dir: str, format: str):
        """Extract archive to directory"""
        
        if format == 'zip':
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        
        elif format == 'rar':
            if not RARFILE_AVAILABLE:
                raise NotImplementedError("RAR support not available. Install rarfile and UnRAR.")
            with rarfile.RarFile(archive_path, 'r') as rar_ref:
                rar_ref.extractall(extract_dir)
        
        elif format == '7z':
            with py7zr.SevenZipFile(archive_path, 'r') as archive:
                archive.extractall(path=extract_dir)
        
        elif format in ('tar', 'tar.gz', 'tgz', 'tar.bz2', 'tbz2'):
            mode = 'r'
            if 'gz' in format or format == 'tgz':
                mode = 'r:gz'
            elif 'bz2' in format or format == 'tbz2':
                mode = 'r:bz2'
            
            with tarfile.open(archive_path, mode) as tar_ref:
                tar_ref.extractall(extract_dir)
        
        elif format == 'gzip' or format == 'gz':
            import gzip
            output_file = os.path.join(extract_dir, 'extracted_file')
            with gzip.open(archive_path, 'rb') as f_in:
                with open(output_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        
        else:
            raise NotImplementedError(f"Extraction from {format} not supported")
    
    @staticmethod
    async def create_archive(source_dir: str, output_path: str, format: str):
        """Create archive from directory"""
        
        if format == 'zip':
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)
        
        elif format == 'rar':
            raise NotImplementedError("RAR creation requires WinRAR command line tools")
        
        elif format == '7z':
            with py7zr.SevenZipFile(output_path, 'w') as archive:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        archive.write(file_path, arcname)
        
        elif format in ('tar', 'tar.gz', 'tgz'):
            mode = 'w:gz' if format in ('tar.gz', 'tgz') else 'w'
            with tarfile.open(output_path, mode) as tar:
                tar.add(source_dir, arcname=os.path.basename(source_dir))
        
        elif format in ('tar.bz2', 'tbz2'):
            with tarfile.open(output_path, 'w:bz2') as tar:
                tar.add(source_dir, arcname=os.path.basename(source_dir))
        
        elif format == 'gzip' or format == 'gz':
            import gzip
            # For single file
            files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
            if files:
                input_file = os.path.join(source_dir, files[0])
                with open(input_file, 'rb') as f_in:
                    with gzip.open(output_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
        
        else:
            raise NotImplementedError(f"Creation of {format} not supported")
    
    @staticmethod
    async def zip_to_rar(input_path: str, output_path: str) -> str:
        """Convert ZIP to RAR"""
        return await ArchiveConverter.convert(input_path, output_path, 'zip', 'rar')
    
    @staticmethod
    async def rar_to_zip(input_path: str, output_path: str) -> str:
        """Convert RAR to ZIP"""
        return await ArchiveConverter.convert(input_path, output_path, 'rar', 'zip')
    
    @staticmethod
    async def seven_z_to_zip(input_path: str, output_path: str) -> str:
        """Convert 7Z to ZIP"""
        return await ArchiveConverter.convert(input_path, output_path, '7z', 'zip')
    
    @staticmethod
    async def tar_to_zip(input_path: str, output_path: str) -> str:
        """Convert TAR to ZIP"""
        return await ArchiveConverter.convert(input_path, output_path, 'tar', 'zip')
    
    @staticmethod
    async def gzip_to_zip(input_path: str, output_path: str) -> str:
        """Convert GZIP to ZIP"""
        return await ArchiveConverter.convert(input_path, output_path, 'gzip', 'zip')
    
    @staticmethod
    async def zip_to_tar(input_path: str, output_path: str) -> str:
        """Convert ZIP to TAR"""
        return await ArchiveConverter.convert(input_path, output_path, 'zip', 'tar')
