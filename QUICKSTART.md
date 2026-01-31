# Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Install packages
pip install fastapi uvicorn[standard] python-multipart aiofiles python-dotenv pydantic pydantic-settings sqlalchemy Pillow PyPDF2 python-docx
```

### 2. Start the Server

**Option A: Using the run script (Windows)**
```bash
cd file_conversion
run.bat
```

**Option B: Manual start**
```bash
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Access the Application

- **Web Interface**: http://localhost:8000/static/index.html
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📱 Using the Web Interface

1. **Upload a File**
   - Drag and drop your file onto the upload area
   - OR click "Choose File" to browse

2. **Select Target Format**
   - Choose a category tab (Documents, Images, etc.)
   - Click on your desired output format

3. **Convert**
   - Click "Convert File"
   - Wait for the conversion to complete
   - Download your converted file!

## 🔌 Using the API

### Upload a File

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@yourfile.pdf"
```

Response:
```json
{
  "id": 1,
  "filename": "yourfile_abc123.pdf",
  "source_format": "pdf",
  "target_format": "",
  "file_size": 2.5,
  "status": "uploaded",
  "created_at": "2024-01-31T14:00:00"
}
```

### Check Status

```bash
curl "http://localhost:8000/api/conversions/1"
```

### List All Conversions

```bash
curl "http://localhost:8000/api/conversions"
```

### Get Supported Formats

```bash
curl "http://localhost:8000/api/formats"
```

### Download File

```bash
curl "http://localhost:8000/api/download/1" -o output.docx
```

## 🐍 Python Example

```python
import requests

# Upload file
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/upload',
        files={'file': f},
        data={'target_format': 'docx'}
    )
    conversion = response.json()
    print(f"Uploaded: {conversion['id']}")

# Check status
status = requests.get(f"http://localhost:8000/api/conversions/{conversion['id']}")
print(status.json())

# Download converted file
download = requests.get(f"http://localhost:8000/api/download/{conversion['id']}")
with open('output.docx', 'wb') as f:
    f.write(download.content)
```

## 📝 Configuration

Edit `backend/.env`:

```env
# Maximum file size in MB
MAX_FILE_SIZE_MB=50

# How long to keep files (hours)
FILE_RETENTION_HOURS=1

# Rate limiting (requests per minute per IP)
RATE_LIMIT_PER_MINUTE=10

# Server port
PORT=8000
```

## 🛠️ Development Status

**Phase 1: Core Infrastructure** ✅ **COMPLETE**
- FastAPI backend with auto-generated docs
- File upload/download system
- Modern responsive web interface
- Rate limiting & security
- Database tracking
- Automatic cleanup

**Phase 2-11: Conversion Services** 🚧 **IN PROGRESS**

The conversion services will be added progressively. Currently, the infrastructure is ready and you can:
- Upload files
- View file information
- Select target formats
- Use the complete API

Actual file conversions will be implemented in the next phases.

## ⚡ Features

- **100+ File Format Support** (implementation in progress)
- **Dual Interface**: Web UI + REST API
- **Security**: Rate limiting, file validation, auto-cleanup
- **Modern UI**: Drag-and-drop, responsive design
- **Auto Documentation**: Swagger UI at `/docs`
- **Fast & Async**: Built with FastAPI
- **Easy to Extend**: Modular architecture

## 🔍 Troubleshooting

### Server won't start
- Make sure port 8000 is not in use
- Check that virtual environment is activated
- Ensure all dependencies are installed

### Can't access web interface
- Verify server is running: `curl http://localhost:8000/health`
- Try http://127.0.0.1:8000/static/index.html

### File upload fails
- Check file size (default limit: 50MB)
- Ensure uploads directory exists
- Check console for errors

## 📚 Next Steps

1. **Test the infrastructure**: Upload files, check API docs
2. **Implement conversions**: Start with document conversions
3. **Add external tools**: Install FFmpeg for audio/video, Tesseract for OCR
4. **Scale up**: Add background workers for heavy conversions

## 🎯 Project Roadmap

Check `plan.md` for the complete implementation roadmap covering all 10 conversion categories and 100+ format types.

---

**Questions?** Check the API documentation at http://localhost:8000/docs
