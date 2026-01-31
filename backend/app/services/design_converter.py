from PIL import Image
import os
from typing import Optional
import io

# Optional dependency
try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except (ImportError, OSError):
    CAIROSVG_AVAILABLE = False

try:
    from psd_tools import PSDImage
    PSD_TOOLS_AVAILABLE = True
except ImportError:
    PSD_TOOLS_AVAILABLE = False

try:
    import ezdxf
    EZDXF_AVAILABLE = True
except ImportError:
    EZDXF_AVAILABLE = False

class DesignConverter:
    """Handles design and CAD file conversions"""
    
    @staticmethod
    async def convert(input_path: str, output_path: str, 
                     source_format: str, target_format: str) -> str:
        """Main conversion dispatcher"""
        
        source_format = source_format.lower().replace('.', '')
        target_format = target_format.lower().replace('.', '')
        
        conversion_key = f"{source_format}_to_{target_format}"
        
        converters = {
            'psd_to_png': DesignConverter.psd_to_image,
            'psd_to_jpg': DesignConverter.psd_to_image,
            'psd_to_jpeg': DesignConverter.psd_to_image,
            'svg_to_pdf': DesignConverter.svg_to_pdf,
            'dxf_to_svg': DesignConverter.dxf_to_svg,
        }
        
        converter_func = converters.get(conversion_key)
        if converter_func:
            return await converter_func(input_path, output_path, target_format)
        
        raise NotImplementedError(f"Conversion from {source_format} to {target_format} not supported")
    
    @staticmethod
    async def psd_to_image(input_path: str, output_path: str, target_format: str = 'png') -> str:
        """Convert PSD to PNG/JPG"""
        if not PSD_TOOLS_AVAILABLE:
            raise NotImplementedError("psd-tools not available")
        
        psd = PSDImage.open(input_path)
        image = psd.topil()
        
        if target_format.lower() in ('jpg', 'jpeg'):
            if image.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                rgb_img.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = rgb_img
            image.save(output_path, 'JPEG', quality=95)
        else:
            image.save(output_path, 'PNG')
        
        return output_path
    
    @staticmethod
    async def svg_to_pdf(input_path: str, output_path: str, target_format: str = 'pdf') -> str:
        """Convert SVG to PDF"""
        if not CAIROSVG_AVAILABLE:
            raise NotImplementedError("SVG conversion requires Cairo library")
        
        pdf_data = cairosvg.svg2pdf(url=input_path)
        
        with open(output_path, 'wb') as f:
            f.write(pdf_data)
        
        return output_path
    
    @staticmethod
    async def dxf_to_svg(input_path: str, output_path: str, target_format: str = 'svg') -> str:
        """Convert DXF to SVG"""
        if not EZDXF_AVAILABLE:
            raise NotImplementedError("ezdxf not available")
        
        doc = ezdxf.readfile(input_path)
        msp = doc.modelspace()
        
        # Simple SVG generation
        svg_content = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">']
        
        for entity in msp:
            if entity.dxftype() == 'LINE':
                start = entity.dxf.start
                end = entity.dxf.end
                svg_content.append(
                    f'<line x1="{start.x}" y1="{start.y}" x2="{end.x}" y2="{end.y}" stroke="black" stroke-width="1"/>'
                )
            elif entity.dxftype() == 'CIRCLE':
                center = entity.dxf.center
                radius = entity.dxf.radius
                svg_content.append(
                    f'<circle cx="{center.x}" cy="{center.y}" r="{radius}" stroke="black" fill="none"/>'
                )
        
        svg_content.append('</svg>')
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(svg_content))
        
        return output_path
