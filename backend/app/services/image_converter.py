from PIL import Image
import io
import os
from typing import Optional
import cv2
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.utils import ImageReader

# Optional dependency - handle if not available
try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except (ImportError, OSError):
    CAIROSVG_AVAILABLE = False

class ImageConverter:
    """Handles all image format conversions"""
    
    @staticmethod
    async def convert(input_path: str, output_path: str, 
                     source_format: str, target_format: str) -> str:
        """Main conversion dispatcher"""
        
        # Normalize formats
        source_format = source_format.lower().replace('.', '')
        target_format = target_format.lower().replace('.', '')
        
        # Route to appropriate converter
        conversion_key = f"{source_format}_to_{target_format}"
        
        converters = {
            # Common formats
            'jpg_to_png': ImageConverter.jpg_to_png,
            'png_to_jpg': ImageConverter.png_to_jpg,
            'jpeg_to_png': ImageConverter.jpg_to_png,
            'png_to_jpeg': ImageConverter.png_to_jpg,
            'jpg_to_webp': ImageConverter.to_webp,
            'jpeg_to_webp': ImageConverter.to_webp,
            'png_to_webp': ImageConverter.to_webp,
            'webp_to_jpg': ImageConverter.from_webp,
            'webp_to_png': ImageConverter.from_webp,
            'tiff_to_jpg': ImageConverter.standard_convert,
            'tiff_to_png': ImageConverter.standard_convert,
            'bmp_to_jpg': ImageConverter.standard_convert,
            'bmp_to_png': ImageConverter.standard_convert,
            'heic_to_jpg': ImageConverter.heic_to_jpg,
            'heic_to_png': ImageConverter.heic_to_png,
            
            # SVG conversions
            'svg_to_png': ImageConverter.svg_to_raster,
            'svg_to_jpg': ImageConverter.svg_to_raster,
            
            # Image to PDF
            'jpg_to_pdf': ImageConverter.image_to_pdf,
            'jpeg_to_pdf': ImageConverter.image_to_pdf,
            'png_to_pdf': ImageConverter.image_to_pdf,
            'webp_to_pdf': ImageConverter.image_to_pdf,
            'tiff_to_pdf': ImageConverter.image_to_pdf,
            'bmp_to_pdf': ImageConverter.image_to_pdf,
            
            # ICO conversions
            'ico_to_png': ImageConverter.standard_convert,
            'png_to_ico': ImageConverter.png_to_ico,
        }
        
        converter_func = converters.get(conversion_key)
        if converter_func:
            return await converter_func(input_path, output_path, target_format)
        
        # Try standard PIL conversion as fallback
        try:
            return await ImageConverter.standard_convert(input_path, output_path, target_format)
        except Exception as e:
            raise NotImplementedError(
                f"Conversion from {source_format} to {target_format} not supported: {str(e)}"
            )
    
    @staticmethod
    async def jpg_to_png(input_path: str, output_path: str, target_format: str = 'png') -> str:
        """Convert JPG to PNG"""
        img = Image.open(input_path)
        # Remove alpha channel if present
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        img.save(output_path, 'PNG')
        return output_path
    
    @staticmethod
    async def png_to_jpg(input_path: str, output_path: str, target_format: str = 'jpg') -> str:
        """Convert PNG to JPG"""
        img = Image.open(input_path)
        # Convert RGBA to RGB
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(output_path, 'JPEG', quality=95)
        return output_path
    
    @staticmethod
    async def to_webp(input_path: str, output_path: str, target_format: str = 'webp') -> str:
        """Convert any image to WebP"""
        img = Image.open(input_path)
        img.save(output_path, 'WEBP', quality=90)
        return output_path
    
    @staticmethod
    async def from_webp(input_path: str, output_path: str, target_format: str) -> str:
        """Convert WebP to other formats"""
        img = Image.open(input_path)
        if target_format.upper() == 'JPG' or target_format.upper() == 'JPEG':
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            img.save(output_path, 'JPEG', quality=95)
        else:
            img.save(output_path, target_format.upper())
        return output_path
    
    @staticmethod
    async def standard_convert(input_path: str, output_path: str, target_format: str) -> str:
        """Standard PIL-based conversion"""
        img = Image.open(input_path)
        
        # Handle alpha channel for formats that don't support it
        if target_format.lower() in ('jpg', 'jpeg', 'bmp') and img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode == 'RGBA':
                rgb_img.paste(img, mask=img.split()[-1])
            else:
                rgb_img.paste(img)
            img = rgb_img
        
        # Save with appropriate format
        save_format = target_format.upper()
        if save_format == 'JPG':
            save_format = 'JPEG'
        
        if save_format == 'JPEG':
            img.save(output_path, save_format, quality=95)
        else:
            img.save(output_path, save_format)
        
        return output_path
    
    @staticmethod
    async def heic_to_jpg(input_path: str, output_path: str, target_format: str = 'jpg') -> str:
        """Convert HEIC to JPG"""
        try:
            import pillow_heif
            heif_file = pillow_heif.read_heif(input_path)
            img = Image.frombytes(
                heif_file.mode, heif_file.size, heif_file.data,
                "raw", heif_file.mode, heif_file.stride
            )
            img.save(output_path, 'JPEG', quality=95)
            return output_path
        except ImportError:
            # Fallback to Pillow if pillow-heif not available
            img = Image.open(input_path)
            img = img.convert('RGB')
            img.save(output_path, 'JPEG', quality=95)
            return output_path
    
    @staticmethod
    async def heic_to_png(input_path: str, output_path: str, target_format: str = 'png') -> str:
        """Convert HEIC to PNG"""
        try:
            import pillow_heif
            heif_file = pillow_heif.read_heif(input_path)
            img = Image.frombytes(
                heif_file.mode, heif_file.size, heif_file.data,
                "raw", heif_file.mode, heif_file.stride
            )
            img.save(output_path, 'PNG')
            return output_path
        except ImportError:
            img = Image.open(input_path)
            img.save(output_path, 'PNG')
            return output_path
    
    @staticmethod
    async def svg_to_raster(input_path: str, output_path: str, target_format: str) -> str:
        """Convert SVG to PNG/JPG using cairosvg"""
        if not CAIROSVG_AVAILABLE:
            raise NotImplementedError("SVG conversion requires Cairo library. Install GTK+ on Windows or cairo on Linux/Mac.")
        
        # First convert SVG to PNG
        png_data = cairosvg.svg2png(url=input_path, scale=2.0)
        
        if target_format.lower() in ('png',):
            with open(output_path, 'wb') as f:
                f.write(png_data)
        else:
            # Convert PNG to JPG
            img = Image.open(io.BytesIO(png_data))
            if img.mode in ('RGBA', 'LA'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1])
                img = rgb_img
            img.save(output_path, 'JPEG', quality=95)
        
        return output_path
    
    @staticmethod
    async def image_to_pdf(input_path: str, output_path: str, target_format: str = 'pdf') -> str:
        """Convert any image to PDF"""
        img = Image.open(input_path)
        
        # Convert to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                if 'transparency' in img.info:
                    rgb_img.paste(img, mask=img.split()[-1])
                else:
                    rgb_img.paste(img)
            img = rgb_img
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Create PDF
        c = pdf_canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        # Scale image to fit page
        img_width, img_height = img.size
        aspect = img_height / float(img_width)
        
        if aspect > 1:  # Portrait
            display_height = height - 40
            display_width = display_height / aspect
        else:  # Landscape
            display_width = width - 40
            display_height = display_width * aspect
        
        # Center image
        x = (width - display_width) / 2
        y = (height - display_height) / 2
        
        # Draw image
        img_reader = ImageReader(img)
        c.drawImage(img_reader, x, y, display_width, display_height)
        c.save()
        
        return output_path
    
    @staticmethod
    async def png_to_ico(input_path: str, output_path: str, target_format: str = 'ico') -> str:
        """Convert PNG to ICO"""
        img = Image.open(input_path)
        
        # ICO supports multiple sizes, create common sizes
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Create list of resized images
        images = []
        for size in sizes:
            if img.size[0] >= size[0] and img.size[1] >= size[1]:
                resized = img.resize(size, Image.Resampling.LANCZOS)
                images.append(resized)
        
        # Save as ICO with multiple sizes
        if images:
            images[0].save(output_path, format='ICO', sizes=[img.size for img in images])
        else:
            img.save(output_path, format='ICO')
        
        return output_path
