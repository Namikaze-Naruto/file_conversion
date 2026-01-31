# 👨‍💻 Developer Guide - File Conversion Platform

Complete guide for developers contributing to the File Conversion Platform.

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Project Architecture](#project-architecture)
3. [Project Structure](#project-structure)
4. [How to Add New Converters](#how-to-add-new-converters)
5. [Code Style Guidelines](#code-style-guidelines)
6. [Testing Approach](#testing-approach)
7. [API Development](#api-development)
8. [Frontend Development](#frontend-development)
9. [Database Schema](#database-schema)
10. [Common Patterns](#common-patterns)
11. [Debugging Tips](#debugging-tips)
12. [Contributing Guidelines](#contributing-guidelines)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ (3.11+ recommended)
- Git
- Code editor (VS Code recommended)
- Basic understanding of FastAPI and async Python

### Development Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd file_conversion

# 2. Create virtual environment
cd backend
python -m venv venv

# Activate virtual environment
# Windows
.\venv\Scripts\Activate.ps1
# Linux/Mac
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install development dependencies
pip install pytest pytest-asyncio pytest-cov black isort mypy

# 5. Copy environment file
cp .env.example .env

# 6. Run development server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### VS Code Configuration

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "100"],
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

---

## 🏗️ Project Architecture

### High-Level Architecture

```
┌─────────────┐
│   Frontend  │  (HTML/CSS/JS)
│  Static UI  │
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────────────────────┐
│      FastAPI Backend         │
│  ┌────────────────────────┐ │
│  │   API Routes           │ │
│  │  (Documents, Images,   │ │
│  │   Audio, Video, etc.)  │ │
│  └───────┬────────────────┘ │
│          │                   │
│  ┌───────▼────────────────┐ │
│  │  Service Layer         │ │
│  │  (Conversion Logic)    │ │
│  └───────┬────────────────┘ │
│          │                   │
│  ┌───────▼────────────────┐ │
│  │  File Handler          │ │
│  │  (I/O Operations)      │ │
│  └───────┬────────────────┘ │
│          │                   │
│  ┌───────▼────────────────┐ │
│  │  Database (SQLite)     │ │
│  │  (Conversion Tracking) │ │
│  └────────────────────────┘ │
└─────────────────────────────┘
```

### Layer Responsibilities

**1. API Routes** (`app/routers/`)
- HTTP request handling
- Request validation
- Response formatting
- Error handling

**2. Service Layer** (`app/services/`)
- Business logic
- Conversion implementation
- External tool integration
- Error handling

**3. Utilities** (`app/utils/`)
- File operations
- Validation
- Helper functions

**4. Middleware** (`app/middleware/`)
- Rate limiting
- CORS
- Authentication (future)

**5. Database** (`app/database.py`, `app/models.py`)
- Data persistence
- Conversion tracking
- SQLAlchemy ORM

---

## 📁 Project Structure

```
file_conversion/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry
│   │   ├── config.py            # Configuration settings
│   │   ├── database.py          # Database setup & models
│   │   ├── models.py            # Pydantic models (API schemas)
│   │   │
│   │   ├── routers/             # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── documents.py     # Document conversion routes
│   │   │   ├── images.py        # Image conversion routes
│   │   │   ├── audio.py         # Audio conversion routes
│   │   │   ├── video.py         # Video conversion routes
│   │   │   ├── archives.py      # Archive conversion routes
│   │   │   ├── code.py          # Code/data conversion routes
│   │   │   ├── design.py        # Design file conversion routes
│   │   │   ├── database_conv.py # Database format routes
│   │   │   ├── security.py      # Security feature routes
│   │   │   └── ai_powered.py    # AI-powered routes
│   │   │
│   │   ├── services/            # Conversion implementations
│   │   │   ├── __init__.py
│   │   │   ├── document_converter.py
│   │   │   ├── image_converter.py
│   │   │   ├── audio_converter.py
│   │   │   ├── video_converter.py
│   │   │   ├── archive_converter.py
│   │   │   ├── code_converter.py
│   │   │   ├── design_converter.py
│   │   │   ├── database_converter.py
│   │   │   ├── security_converter.py
│   │   │   └── ai_converter.py
│   │   │
│   │   ├── utils/               # Utility functions
│   │   │   ├── __init__.py
│   │   │   ├── file_handler.py  # File I/O operations
│   │   │   ├── validators.py    # Format validation
│   │   │   └── cleanup.py       # File cleanup tasks
│   │   │
│   │   └── middleware/          # Custom middleware
│   │       ├── __init__.py
│   │       └── rate_limiter.py  # Rate limiting
│   │
│   ├── tests/                   # Test suite
│   │   ├── __init__.py
│   │   ├── test_documents.py
│   │   ├── test_images.py
│   │   └── ...
│   │
│   ├── uploads/                 # Temporary upload storage
│   ├── outputs/                 # Converted file storage
│   ├── logs/                    # Application logs
│   ├── requirements.txt         # Python dependencies
│   ├── .env                     # Environment variables
│   └── .env.example             # Example configuration
│
├── frontend/                    # Web interface
│   ├── index.html               # Main HTML file
│   ├── css/
│   │   └── style.css            # Styles
│   ├── js/
│   │   ├── app.js               # Main application logic
│   │   ├── api.js               # API communication
│   │   └── ui.js                # UI updates
│   └── assets/                  # Images, icons
│
├── docs/                        # Documentation
│   ├── API.md
│   └── DEVELOPMENT.md
│
├── README.md
├── QUICKSTART.md
└── .gitignore
```

---

## ➕ How to Add New Converters

### Step-by-Step Guide

#### 1. Identify the Category

Determine which category your converter belongs to:
- `documents` - PDF, Word, Excel, etc.
- `images` - JPG, PNG, WebP, etc.
- `audio` - MP3, WAV, AAC, etc.
- `video` - MP4, MKV, AVI, etc.
- `archives` - ZIP, RAR, 7Z, etc.
- `code` - JSON, XML, YAML, etc.
- `design` - PSD, AI, SVG, etc.
- `database` - SQL, Parquet, Avro, etc.
- `security` - Encryption, hashing, etc.
- `ai_powered` - OCR, transcription, etc.

#### 2. Update Validators

Add supported formats to `app/utils/validators.py`:

```python
SUPPORTED_FORMATS: Dict[str, Set[str]] = {
    "document": {
        "pdf", "doc", "docx", "txt", "rtf", "odt",
        "newformat"  # Add your new format here
    },
    # ... other categories
}
```

#### 3. Implement Conversion Logic

Add conversion method to the appropriate service file (e.g., `app/services/document_converter.py`):

```python
class DocumentConverter:
    @staticmethod
    async def convert(input_path: str, output_path: str, 
                     source_format: str, target_format: str) -> str:
        """Convert document from source to target format"""
        
        source_format = source_format.lower()
        target_format = target_format.lower()
        
        # Add your conversion case
        if source_format == 'newformat':
            if target_format == 'pdf':
                return await DocumentConverter.newformat_to_pdf(input_path, output_path)
        
        # ... existing conversions
        
        raise HTTPException(
            status_code=400,
            detail=f"Conversion from {source_format} to {target_format} not supported"
        )
    
    @staticmethod
    async def newformat_to_pdf(input_path: str, output_path: str) -> str:
        """Convert NEWFORMAT to PDF"""
        try:
            # Your conversion implementation
            # Example using an external library
            from newformat_lib import Converter
            
            converter = Converter(input_path)
            converter.save_as_pdf(output_path)
            
            return output_path
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Conversion failed: {str(e)}"
            )
```

#### 4. Add Route (if needed)

If creating a new category, add a router in `app/routers/`:

```python
# app/routers/newcategory.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, Conversion
from app.services.newcategory_converter import NewCategoryConverter
from app.models import ConversionResponse

router = APIRouter(prefix="/api/newcategory", tags=["New Category"])

@router.post("/convert/{conversion_id}", response_model=ConversionResponse)
async def convert_newcategory(
    conversion_id: int,
    target_format: str,
    db: Session = Depends(get_db)
):
    """Convert new category files"""
    
    # Get conversion record
    conversion = db.query(Conversion).filter(Conversion.id == conversion_id).first()
    
    if not conversion:
        raise HTTPException(status_code=404, detail="Conversion not found")
    
    try:
        # Perform conversion
        output_path = await NewCategoryConverter.convert(
            input_path=conversion.file_path,
            output_path=f"outputs/{conversion.id}_output.{target_format}",
            source_format=conversion.source_format,
            target_format=target_format
        )
        
        # Update database
        conversion.target_format = target_format
        conversion.output_path = output_path
        conversion.status = "completed"
        db.commit()
        db.refresh(conversion)
        
        return conversion
        
    except Exception as e:
        conversion.status = "failed"
        conversion.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))
```

#### 5. Register Router

Add your router to `app/main.py`:

```python
from app.routers import (
    documents, images, audio, video, 
    archives, code, design, database_conv, 
    security, ai_powered, newcategory  # Add your new router
)

# Include routers
app.include_router(newcategory.router)
```

#### 6. Update Frontend

Add the new format to `frontend/js/app.js`:

```javascript
const formatsByCategory = {
    'Documents': ['pdf', 'docx', 'txt', 'newformat'],  // Add here
    'Images': ['jpg', 'png', 'webp'],
    // ... other categories
};
```

#### 7. Add Tests

Create tests in `backend/tests/test_newcategory.py`:

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_newformat_to_pdf():
    """Test NEWFORMAT to PDF conversion"""
    
    # Upload file
    with open("test_files/sample.newformat", "rb") as f:
        response = client.post("/api/upload", files={"file": f})
    
    assert response.status_code == 200
    conversion_id = response.json()["id"]
    
    # Convert
    response = client.post(
        f"/api/newcategory/convert/{conversion_id}?target_format=pdf"
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    
    # Download
    response = client.get(f"/api/download/{conversion_id}")
    assert response.status_code == 200
```

#### 8. Document Your Converter

Add documentation to your converter docstrings:

```python
async def newformat_to_pdf(input_path: str, output_path: str) -> str:
    """
    Convert NEWFORMAT to PDF
    
    Args:
        input_path: Path to input .newformat file
        output_path: Path to save output PDF file
        
    Returns:
        str: Path to the converted PDF file
        
    Raises:
        HTTPException: If conversion fails
        
    Example:
        >>> await NewCategoryConverter.newformat_to_pdf("input.newformat", "output.pdf")
        "output.pdf"
        
    Notes:
        - Requires newformat_lib package
        - Supports NEWFORMAT v2.0 and above
        - Maximum file size: 50MB
    """
```

---

## 🎨 Code Style Guidelines

### Python Style (PEP 8)

```python
# Use Black formatter (line length 100)
# Use isort for import sorting

# Good: Clear naming
async def convert_pdf_to_docx(input_path: str, output_path: str) -> str:
    """Convert PDF to DOCX with proper formatting."""
    pass

# Bad: Unclear naming
async def conv(i: str, o: str) -> str:
    pass

# Good: Type hints
def process_file(file_path: str, options: Dict[str, Any]) -> Optional[Path]:
    pass

# Bad: No type hints
def process_file(file_path, options):
    pass

# Good: Async when I/O bound
async def read_large_file(path: str) -> bytes:
    async with aiofiles.open(path, 'rb') as f:
        return await f.read()

# Good: Error handling
try:
    result = await converter.convert(input_path, output_path)
except ConversionError as e:
    logger.error(f"Conversion failed: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case()`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore()`

### Import Order

```python
# 1. Standard library
import os
from pathlib import Path
from typing import Dict, List, Optional

# 2. Third-party
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

# 3. Local application
from app.config import settings
from app.database import get_db
from app.models import ConversionResponse
```

### Docstrings

Use Google-style docstrings:

```python
def convert_file(input_path: str, output_format: str) -> str:
    """
    Convert a file to the specified output format.
    
    This function handles file conversion by delegating to the appropriate
    converter based on the file type.
    
    Args:
        input_path: Path to the input file
        output_format: Desired output format (e.g., 'pdf', 'docx')
        
    Returns:
        Path to the converted file
        
    Raises:
        HTTPException: If conversion fails or format is unsupported
        
    Example:
        >>> convert_file('/path/to/input.txt', 'pdf')
        '/path/to/output.pdf'
    """
    pass
```

---

## 🧪 Testing Approach

### Test Structure

```
backend/tests/
├── __init__.py
├── conftest.py              # Pytest fixtures
├── test_documents.py        # Document conversion tests
├── test_images.py           # Image conversion tests
├── test_api.py              # API endpoint tests
├── test_validators.py       # Validation tests
└── fixtures/                # Test files
    ├── sample.pdf
    ├── sample.docx
    └── sample.jpg
```

### Writing Tests

```python
# conftest.py - Shared fixtures
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)

@pytest.fixture
def sample_pdf():
    """Sample PDF file fixture"""
    return "tests/fixtures/sample.pdf"

# test_documents.py
import pytest
from fastapi.testclient import TestClient

def test_upload_file(client):
    """Test file upload endpoint"""
    with open("tests/fixtures/sample.pdf", "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": ("test.pdf", f, "application/pdf")}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["source_format"] == "pdf"

def test_pdf_to_docx_conversion(client, sample_pdf):
    """Test PDF to DOCX conversion"""
    # Upload
    with open(sample_pdf, "rb") as f:
        upload_response = client.post(
            "/api/upload",
            files={"file": f}
        )
    
    conversion_id = upload_response.json()["id"]
    
    # Convert
    convert_response = client.post(
        f"/api/documents/convert/{conversion_id}?target_format=docx"
    )
    
    assert convert_response.status_code == 200
    assert convert_response.json()["status"] == "completed"

@pytest.mark.asyncio
async def test_async_conversion():
    """Test async conversion function"""
    from app.services.document_converter import DocumentConverter
    
    result = await DocumentConverter.pdf_to_txt(
        "tests/fixtures/sample.pdf",
        "tests/outputs/output.txt"
    )
    
    assert result is not None
    assert os.path.exists(result)
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_documents.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_documents.py::test_upload_file
```

---

## 🔌 API Development

### Creating New Endpoints

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ConversionResponse, ErrorResponse

router = APIRouter(prefix="/api/category", tags=["Category Name"])

@router.post(
    "/convert/{conversion_id}",
    response_model=ConversionResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Convert file in category",
    description="Detailed description of what this endpoint does"
)
async def convert_file(
    conversion_id: int,
    target_format: str = Query(..., description="Target file format"),
    quality: int = Query(95, ge=1, le=100, description="Output quality (1-100)"),
    db: Session = Depends(get_db)
):
    """
    Convert a file to the specified format.
    
    - **conversion_id**: ID from upload response
    - **target_format**: Desired output format
    - **quality**: Output quality (optional, default 95)
    """
    # Implementation
    pass
```

### Response Models

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ConversionResponse(BaseModel):
    id: int
    original_filename: str
    source_format: str
    target_format: Optional[str] = None
    status: str = Field(..., description="Status: uploaded, processing, completed, failed")
    progress: Optional[int] = Field(None, ge=0, le=100)
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    file_size: int
    
    class Config:
        from_attributes = True
```

---

## 🎨 Frontend Development

### Adding New Features

```javascript
// frontend/js/app.js

// Add new format category
const formatsByCategory = {
    'New Category': ['format1', 'format2', 'format3']
};

// Add conversion handler
async function convertFile(conversionId, targetFormat) {
    try {
        const response = await fetch(
            `${API_BASE}/newcategory/convert/${conversionId}?target_format=${targetFormat}`,
            { method: 'POST' }
        );
        
        if (!response.ok) {
            throw new Error('Conversion failed');
        }
        
        const data = await response.json();
        return data;
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message);
    }
}
```

---

## 💾 Database Schema

### Conversion Table

```python
class Conversion(Base):
    __tablename__ = "conversions"
    
    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    source_format = Column(String, nullable=False)
    target_format = Column(String, nullable=True)
    status = Column(String, default="uploaded")
    output_path = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    file_size = Column(Integer)
    ip_address = Column(String, nullable=True)
```

---

## 🐛 Debugging Tips

### Enable Debug Logging

```python
# app/config.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### FastAPI Debug Mode

```bash
# Run with auto-reload and debug info
uvicorn app.main:app --reload --log-level debug
```

### Using Debugger

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or with IPython
import IPython; IPython.embed()
```

---

## 🤝 Contributing Guidelines

1. **Fork** the repository
2. Create a **feature branch**: `git checkout -b feature/new-converter`
3. **Make your changes** following the style guidelines
4. **Write tests** for new features
5. **Run tests**: `pytest`
6. **Format code**: `black . && isort .`
7. **Commit**: `git commit -m "Add: New converter for XYZ format"`
8. **Push**: `git push origin feature/new-converter`
9. Create a **Pull Request**

### Commit Message Convention

```
Type: Short description

Longer description if needed

Types:
- Add: New feature
- Fix: Bug fix
- Update: Update existing feature
- Remove: Remove feature
- Refactor: Code refactoring
- Docs: Documentation changes
- Test: Add or update tests
```

---

**Happy Coding! 🎉**

*Developer Guide v1.0.0 - Last Updated: January 2026*
