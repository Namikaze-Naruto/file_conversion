import base64
import hashlib
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import PyPDF2
from typing import Optional

class SecurityConverter:
    """Handles security, encoding, and encryption conversions"""
    
    @staticmethod
    async def convert(input_path: str, output_path: str, 
                     source_format: str, target_format: str, **kwargs) -> str:
        """Main conversion dispatcher"""
        
        source_format = source_format.lower().replace('.', '')
        target_format = target_format.lower().replace('.', '')
        
        # Special handling for security operations
        if source_format == 'file' and target_format == 'base64':
            return await SecurityConverter.file_to_base64(input_path, output_path)
        elif source_format == 'base64' and target_format == 'file':
            return await SecurityConverter.base64_to_file(input_path, output_path)
        elif target_format == 'hash':
            algorithm = kwargs.get('algorithm', 'sha256')
            return await SecurityConverter.generate_hash(input_path, output_path, algorithm)
        elif target_format == 'encrypted':
            password = kwargs.get('password', 'default_password')
            return await SecurityConverter.encrypt_file(input_path, output_path, password)
        elif source_format == 'encrypted':
            password = kwargs.get('password', 'default_password')
            return await SecurityConverter.decrypt_file(input_path, output_path, password)
        elif 'pdf' in source_format and target_format == 'locked':
            password = kwargs.get('password', 'default_password')
            return await SecurityConverter.lock_pdf(input_path, output_path, password)
        elif source_format == 'locked' and 'pdf' in target_format:
            password = kwargs.get('password', '')
            return await SecurityConverter.unlock_pdf(input_path, output_path, password)
        
        raise NotImplementedError(f"Conversion from {source_format} to {target_format} not supported")
    
    @staticmethod
    async def file_to_base64(input_path: str, output_path: str) -> str:
        """Encode file to Base64"""
        with open(input_path, 'rb') as f:
            file_data = f.read()
        
        encoded = base64.b64encode(file_data).decode('utf-8')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(encoded)
        
        return output_path
    
    @staticmethod
    async def base64_to_file(input_path: str, output_path: str) -> str:
        """Decode Base64 to file"""
        with open(input_path, 'r', encoding='utf-8') as f:
            encoded = f.read()
        
        decoded = base64.b64decode(encoded)
        
        with open(output_path, 'wb') as f:
            f.write(decoded)
        
        return output_path
    
    @staticmethod
    async def generate_hash(input_path: str, output_path: str, algorithm: str = 'sha256') -> str:
        """Generate hash of file"""
        with open(input_path, 'rb') as f:
            file_data = f.read()
        
        if algorithm.lower() == 'md5':
            hash_obj = hashlib.md5(file_data)
        elif algorithm.lower() == 'sha256':
            hash_obj = hashlib.sha256(file_data)
        elif algorithm.lower() == 'sha1':
            hash_obj = hashlib.sha1(file_data)
        elif algorithm.lower() == 'sha512':
            hash_obj = hashlib.sha512(file_data)
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        
        hash_value = hash_obj.hexdigest()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"{algorithm.upper()}: {hash_value}\n")
            f.write(f"File: {os.path.basename(input_path)}\n")
        
        return output_path
    
    @staticmethod
    async def encrypt_file(input_path: str, output_path: str, password: str) -> str:
        """Encrypt file using Fernet (symmetric encryption)"""
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'file_converter_salt',  # In production, use random salt
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        fernet = Fernet(key)
        
        with open(input_path, 'rb') as f:
            file_data = f.read()
        
        encrypted = fernet.encrypt(file_data)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted)
        
        return output_path
    
    @staticmethod
    async def decrypt_file(input_path: str, output_path: str, password: str) -> str:
        """Decrypt file using Fernet"""
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'file_converter_salt',
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        fernet = Fernet(key)
        
        with open(input_path, 'rb') as f:
            encrypted_data = f.read()
        
        try:
            decrypted = fernet.decrypt(encrypted_data)
        except Exception:
            raise ValueError("Decryption failed. Check password.")
        
        with open(output_path, 'wb') as f:
            f.write(decrypted)
        
        return output_path
    
    @staticmethod
    async def lock_pdf(input_path: str, output_path: str, password: str) -> str:
        """Password-protect a PDF"""
        pdf_reader = PyPDF2.PdfReader(input_path)
        pdf_writer = PyPDF2.PdfWriter()
        
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)
        
        pdf_writer.encrypt(password)
        
        with open(output_path, 'wb') as f:
            pdf_writer.write(f)
        
        return output_path
    
    @staticmethod
    async def unlock_pdf(input_path: str, output_path: str, password: str) -> str:
        """Remove password protection from PDF"""
        pdf_reader = PyPDF2.PdfReader(input_path)
        
        if pdf_reader.is_encrypted:
            if not pdf_reader.decrypt(password):
                raise ValueError("Invalid password for PDF")
        
        pdf_writer = PyPDF2.PdfWriter()
        
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)
        
        with open(output_path, 'wb') as f:
            pdf_writer.write(f)
        
        return output_path
