import json
import csv
import yaml
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from typing import Any, Dict, List
import pandas as pd
from bs4 import BeautifulSoup
import markdown
import os

try:
    from nbconvert import HTMLExporter, PDFExporter
    from nbformat import read as nb_read
    NBCONVERT_AVAILABLE = True
except ImportError:
    NBCONVERT_AVAILABLE = False

class CodeConverter:
    """Handles code and data format conversions"""
    
    @staticmethod
    async def convert(input_path: str, output_path: str, 
                     source_format: str, target_format: str) -> str:
        """Main conversion dispatcher"""
        
        source_format = source_format.lower().replace('.', '')
        target_format = target_format.lower().replace('.', '')
        
        conversion_key = f"{source_format}_to_{target_format}"
        
        converters = {
            'json_to_csv': CodeConverter.json_to_csv,
            'csv_to_json': CodeConverter.csv_to_json,
            'json_to_xml': CodeConverter.json_to_xml,
            'xml_to_json': CodeConverter.xml_to_json,
            'csv_to_xml': CodeConverter.csv_to_xml,
            'xml_to_csv': CodeConverter.xml_to_csv,
            'json_to_yaml': CodeConverter.json_to_yaml,
            'yaml_to_json': CodeConverter.yaml_to_json,
            'xlsx_to_json': CodeConverter.excel_to_json,
            'xls_to_json': CodeConverter.excel_to_json,
            'html_to_pdf': CodeConverter.html_to_pdf,
            'html_to_markdown': CodeConverter.html_to_markdown,
            'md_to_html': CodeConverter.markdown_to_html,
            'markdown_to_html': CodeConverter.markdown_to_html,
            'ipynb_to_html': CodeConverter.notebook_to_html,
            'ipynb_to_pdf': CodeConverter.notebook_to_pdf,
        }
        
        converter_func = converters.get(conversion_key)
        if converter_func:
            return await converter_func(input_path, output_path)
        
        raise NotImplementedError(f"Conversion from {source_format} to {target_format} not supported")
    
    @staticmethod
    async def json_to_csv(input_path: str, output_path: str) -> str:
        """Convert JSON to CSV"""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle list of dicts
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            raise ValueError("JSON must be a list or dict")
        
        df.to_csv(output_path, index=False)
        return output_path
    
    @staticmethod
    async def csv_to_json(input_path: str, output_path: str) -> str:
        """Convert CSV to JSON"""
        df = pd.read_csv(input_path)
        data = df.to_dict(orient='records')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    @staticmethod
    async def json_to_xml(input_path: str, output_path: str) -> str:
        """Convert JSON to XML"""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        def dict_to_xml(tag, d):
            elem = ET.Element(tag)
            if isinstance(d, dict):
                for key, val in d.items():
                    child = dict_to_xml(key, val)
                    elem.append(child)
            elif isinstance(d, list):
                for item in d:
                    child = dict_to_xml('item', item)
                    elem.append(child)
            else:
                elem.text = str(d)
            return elem
        
        root = dict_to_xml('root', data)
        tree = ET.ElementTree(root)
        
        # Pretty print
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)
        
        return output_path
    
    @staticmethod
    async def xml_to_json(input_path: str, output_path: str) -> str:
        """Convert XML to JSON"""
        def xml_to_dict(element):
            if len(element) == 0:
                return element.text
            result = {}
            for child in element:
                child_data = xml_to_dict(child)
                if child.tag in result:
                    if isinstance(result[child.tag], list):
                        result[child.tag].append(child_data)
                    else:
                        result[child.tag] = [result[child.tag], child_data]
                else:
                    result[child.tag] = child_data
            return result
        
        tree = ET.parse(input_path)
        root = tree.getroot()
        data = {root.tag: xml_to_dict(root)}
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    @staticmethod
    async def csv_to_xml(input_path: str, output_path: str) -> str:
        """Convert CSV to XML"""
        df = pd.read_csv(input_path)
        data = df.to_dict(orient='records')
        
        root = ET.Element('data')
        for row in data:
            record = ET.SubElement(root, 'record')
            for key, value in row.items():
                field = ET.SubElement(record, key)
                field.text = str(value)
        
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)
        
        return output_path
    
    @staticmethod
    async def xml_to_csv(input_path: str, output_path: str) -> str:
        """Convert XML to CSV"""
        tree = ET.parse(input_path)
        root = tree.getroot()
        
        data = []
        for record in root:
            row = {}
            for field in record:
                row[field.tag] = field.text
            data.append(row)
        
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        return output_path
    
    @staticmethod
    async def json_to_yaml(input_path: str, output_path: str) -> str:
        """Convert JSON to YAML"""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        
        return output_path
    
    @staticmethod
    async def yaml_to_json(input_path: str, output_path: str) -> str:
        """Convert YAML to JSON"""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    @staticmethod
    async def excel_to_json(input_path: str, output_path: str) -> str:
        """Convert Excel to JSON"""
        df = pd.read_excel(input_path)
        data = df.to_dict(orient='records')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    @staticmethod
    async def html_to_pdf(input_path: str, output_path: str) -> str:
        """Convert HTML to PDF"""
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        with open(input_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Extract text from HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        
        # Create PDF
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        y = height - 40
        for line in text.split('\n'):
            if y < 40:
                c.showPage()
                y = height - 40
            c.drawString(40, y, line[:80])  # Truncate long lines
            y -= 15
        
        c.save()
        return output_path
    
    @staticmethod
    async def html_to_markdown(input_path: str, output_path: str) -> str:
        """Convert HTML to Markdown"""
        with open(input_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Simple conversion (could be enhanced)
        md_content = soup.get_text()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return output_path
    
    @staticmethod
    async def markdown_to_html(input_path: str, output_path: str) -> str:
        """Convert Markdown to HTML"""
        with open(input_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        html_content = markdown.markdown(md_content, extensions=['extra', 'codehilite'])
        
        # Wrap in HTML template
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Converted Document</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        code {{ background: #f4f4f4; padding: 2px 5px; }}
        pre {{ background: #f4f4f4; padding: 10px; overflow-x: auto; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        return output_path
    
    @staticmethod
    async def notebook_to_html(input_path: str, output_path: str) -> str:
        """Convert Jupyter notebook to HTML"""
        if not NBCONVERT_AVAILABLE:
            raise NotImplementedError("nbconvert not available")
        
        with open(input_path, 'r', encoding='utf-8') as f:
            notebook = nb_read(f, as_version=4)
        
        html_exporter = HTMLExporter()
        body, resources = html_exporter.from_notebook_node(notebook)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(body)
        
        return output_path
    
    @staticmethod
    async def notebook_to_pdf(input_path: str, output_path: str) -> str:
        """Convert Jupyter notebook to PDF"""
        # First convert to HTML then use simpler PDF conversion
        html_path = output_path.replace('.pdf', '_temp.html')
        await CodeConverter.notebook_to_html(input_path, html_path)
        result = await CodeConverter.html_to_pdf(html_path, output_path)
        if os.path.exists(html_path):
            os.remove(html_path)
        return result
