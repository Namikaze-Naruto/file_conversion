import pytesseract
from PIL import Image
import os
from typing import Optional
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.utils import ImageReader
import cv2
import numpy as np

class AIConverter:
    """Handles AI-powered conversions like OCR and text extraction"""
    
    @staticmethod
    async def convert(input_path: str, output_path: str, 
                     source_format: str, target_format: str) -> str:
        """Main conversion dispatcher"""
        
        source_format = source_format.lower().replace('.', '')
        target_format = target_format.lower().replace('.', '')
        
        # Route based on conversion type
        if target_format == 'txt' and source_format in ('png', 'jpg', 'jpeg', 'tiff', 'bmp'):
            return await AIConverter.image_to_text_ocr(input_path, output_path)
        elif source_format == 'pdf' and target_format == 'searchable_pdf':
            return await AIConverter.pdf_to_searchable(input_path, output_path)
        elif source_format == 'pdf' and target_format == 'txt':
            return await AIConverter.pdf_to_text_ocr(input_path, output_path)
        elif target_format == 'json' and source_format in ('png', 'jpg', 'jpeg', 'pdf'):
            return await AIConverter.document_to_structured_json(input_path, output_path, source_format)
        
        raise NotImplementedError(f"AI conversion from {source_format} to {target_format} not supported")
    
    @staticmethod
    async def image_to_text_ocr(input_path: str, output_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(input_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Perform OCR
            text = pytesseract.image_to_string(image, lang='eng')
            
            if not text.strip():
                text = "[No text detected in image]"
            
            # Save extracted text
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            return output_path
            
        except pytesseract.TesseractNotFoundError:
            raise RuntimeError(
                "Tesseract OCR not found. Please install Tesseract OCR:\n"
                "Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki\n"
                "Linux: sudo apt-get install tesseract-ocr\n"
                "Mac: brew install tesseract"
            )
    
    @staticmethod
    async def pdf_to_text_ocr(input_path: str, output_path: str) -> str:
        """Extract text from PDF using OCR (for scanned PDFs)"""
        try:
            # First try regular text extraction
            text_content = []
            
            pdf_reader = PyPDF2.PdfReader(input_path)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text.strip():
                    text_content.append(text)
            
            # If no text found, it might be a scanned PDF - use OCR
            if not text_content or len(''.join(text_content).strip()) < 50:
                # Convert PDF pages to images and OCR them
                import pdf2image
                images = pdf2image.convert_from_path(input_path)
                
                for i, image in enumerate(images):
                    page_text = pytesseract.image_to_string(image, lang='eng')
                    if page_text.strip():
                        text_content.append(f"\n--- Page {i+1} ---\n{page_text}")
            
            final_text = '\n'.join(text_content) if text_content else "[No text detected in PDF]"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_text)
            
            return output_path
            
        except Exception as e:
            # Fallback to basic PDF text extraction
            pdf_reader = PyPDF2.PdfReader(input_path)
            text_content = []
            for page in pdf_reader.pages:
                text_content.append(page.extract_text())
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(text_content))
            
            return output_path
    
    @staticmethod
    async def pdf_to_searchable(input_path: str, output_path: str) -> str:
        """Convert scanned PDF to searchable PDF using OCR"""
        try:
            import pdf2image
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            # Convert PDF pages to images
            images = pdf2image.convert_from_path(input_path, dpi=300)
            
            # Create new PDF with OCR'd text
            c = pdf_canvas.Canvas(output_path, pagesize=letter)
            width, height = letter
            
            for i, image in enumerate(images):
                # OCR the image
                text = pytesseract.image_to_string(image, lang='eng')
                
                # Add image to PDF
                img_path = f"temp_page_{i}.png"
                image.save(img_path, 'PNG')
                
                c.drawImage(img_path, 0, 0, width, height)
                
                # Add invisible text layer for searchability
                text_object = c.beginText(0, height)
                text_object.setFont("Helvetica", 0.1)  # Invisible font size
                text_object.setTextRenderMode(3)  # Invisible text
                text_object.textLines(text)
                c.drawText(text_object)
                
                c.showPage()
                
                # Cleanup temp file
                if os.path.exists(img_path):
                    os.remove(img_path)
            
            c.save()
            return output_path
            
        except ImportError:
            raise RuntimeError("pdf2image library required for this conversion")
    
    @staticmethod
    async def document_to_structured_json(input_path: str, output_path: str, source_format: str) -> str:
        """Convert document to structured JSON with OCR data"""
        import json
        
        if source_format == 'pdf':
            # Extract text from PDF
            pdf_reader = PyPDF2.PdfReader(input_path)
            pages = []
            
            for i, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                pages.append({
                    'page_number': i + 1,
                    'text': text.strip(),
                    'word_count': len(text.split())
                })
            
            result = {
                'document_type': 'pdf',
                'total_pages': len(pages),
                'pages': pages
            }
            
        else:
            # Image OCR
            image = Image.open(input_path)
            
            # Get detailed OCR data
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, lang='eng')
            
            # Structure the data
            words = []
            for i in range(len(ocr_data['text'])):
                if ocr_data['text'][i].strip():
                    words.append({
                        'text': ocr_data['text'][i],
                        'confidence': ocr_data['conf'][i],
                        'left': ocr_data['left'][i],
                        'top': ocr_data['top'][i],
                        'width': ocr_data['width'][i],
                        'height': ocr_data['height'][i]
                    })
            
            full_text = pytesseract.image_to_string(image, lang='eng')
            
            result = {
                'document_type': 'image',
                'image_size': image.size,
                'full_text': full_text,
                'word_count': len(full_text.split()),
                'words': words
            }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    @staticmethod
    async def handwritten_to_text(input_path: str, output_path: str) -> str:
        """Convert handwritten text to digital text using OCR"""
        # Use OCR with special configuration for handwriting
        image = Image.open(input_path)
        
        # Preprocess image for better handwriting recognition
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Convert back to PIL Image
        processed_image = Image.fromarray(thresh)
        
        # OCR with custom configuration
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(processed_image, config=custom_config, lang='eng')
        
        if not text.strip():
            text = "[No handwritten text detected or text is unclear]"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return output_path
