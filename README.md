# 🔄 File Conversion Platform

A comprehensive file conversion platform supporting 100+ conversion types across 10 categories. Convert documents, images, audio, video, archives, code files, and more with both API and web interface.

## ✨ Features

### Supported Conversions

#### 📄 Document Conversions
- PDF ↔ DOC/DOCX/TXT/RTF
- Office: DOCX ↔ ODT, XLS ↔ XLSX, CSV conversions
- PowerPoint: PPT ↔ PPTX, presentations to PDF
- eBooks: PDF/EPUB/MOBI/AZW conversions

#### 🖼️ Image Conversions
- Common formats: JPG ↔ PNG ↔ WebP
- Advanced: TIFF, BMP, HEIC, SVG
- Image ↔ PDF
- ICO conversions
- RAW format support (CR2, NEF, ARW)

#### 🎵 Audio Conversions
- MP3 ↔ WAV ↔ AAC ↔ OGG
- FLAC, M4A, OPUS support
- Speech-to-Text (STT)
- Text-to-Speech (TTS)
- Video → Audio extraction

#### 🎬 Video Conversions
- MP4 ↔ MKV ↔ AVI ↔ MOV
- FLV, WMV, WebM support
- Video → GIF
- Video → Audio
- Video → Frames

#### 📦 Archive Conversions
- ZIP ↔ RAR ↔ 7Z
- TAR, GZIP support

#### 💻 Code & Developer
- JSON ↔ CSV ↔ XML
- YAML ↔ JSON
- Excel ↔ JSON/SQL
- HTML ↔ Markdown
- Jupyter notebooks (ipynb) conversions

#### 🎨 Design & CAD
- PSD → PNG/JPG
- AI → SVG
- SVG → PDF
- DWG/DXF conversions

#### 🗄️ Database
- SQL ↔ CSV
- JSON → SQL
- Parquet → CSV
- Avro → JSON

#### 🔒 Security & Encoding
- Base64 ↔ File
- Hash generation (MD5, SHA256)
- File encryption/decryption
- PDF lock/unlock

#### 🤖 AI-Powered (Coming Soon)
- Image → Text (OCR)
- PDF → Searchable PDF
- Handwritten → Text
- Audio/Video summarization

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- FFmpeg (for audio/video conversions)
- Tesseract OCR (for OCR features)

### Installation

1. **Clone or navigate to the project directory**
```bash
cd file_conversion
```

2. **Set up backend**
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

3. **Start the server**
```bash
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. **Access the application**
- Web Interface: http://localhost:8000/static/index.html
- API Documentation: http://localhost:8000/docs
- Alternative API Docs: http://localhost:8000/redoc

## 📚 API Usage

### Upload a File
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@yourfile.pdf" \
  -F "target_format=docx"
```

### Check Conversion Status
```bash
curl "http://localhost:8000/api/conversions/{conversion_id}"
```

### Download Converted File
```bash
curl "http://localhost:8000/api/download/{conversion_id}" -o output.docx
```

### Get Supported Formats
```bash
curl "http://localhost:8000/api/formats"
```

## 🔧 Configuration

Edit `backend/.env` to configure:

```env
# File Settings
MAX_FILE_SIZE_MB=50
FILE_RETENTION_HOURS=1

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10

# Server
PORT=8000
DEBUG=True
```

## 📁 Project Structure

```
file_conversion/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # Database setup
│   │   ├── models.py            # Pydantic models
│   │   ├── routers/             # API routes (to be added)
│   │   ├── services/            # Conversion logic (to be added)
│   │   ├── utils/               # Helper functions
│   │   └── middleware/          # Rate limiting, etc.
│   ├── uploads/                 # Temporary uploads
│   ├── outputs/                 # Converted files
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── css/
    ├── js/
    └── assets/
```

## 🛠️ Development Status

### ✅ Completed (Phase 1)
- [x] Project structure and setup
- [x] FastAPI application with CORS
- [x] File upload/download endpoints
- [x] File validation and size limits
- [x] Database schema for tracking
- [x] Rate limiting middleware
- [x] Automatic file cleanup
- [x] Modern responsive frontend
- [x] Drag-and-drop file upload

### 🚧 In Progress
- [ ] Document conversion services
- [ ] Image conversion services
- [ ] Audio conversion services
- [ ] Video conversion services
- [ ] Archive conversion services
- [ ] Code/Data conversion services
- [ ] AI-powered conversions

## 🔒 Security Features

- File size validation (50MB default limit)
- Rate limiting (10 requests/minute per IP)
- Automatic file cleanup (1 hour retention)
- CORS protection
- Input validation

## 📝 License

MIT License - Feel free to use this project for personal or commercial purposes.

## 🤝 Contributing

Contributions are welcome! This is an ongoing project with many conversion types to implement.

## 📞 Support

For issues or questions, please check the API documentation at `/docs` or open an issue.

---

**Current Version**: 1.0.0  
**Status**: Phase 1 Complete - Core infrastructure ready. Conversion services to be implemented in subsequent phases.
