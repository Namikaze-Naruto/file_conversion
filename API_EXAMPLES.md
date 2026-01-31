# 🔌 API Examples - File Conversion Platform

Complete API reference with examples in cURL, Python, and JavaScript.

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Rate Limits](#rate-limits)
4. [Upload File](#upload-file)
5. [Convert File](#convert-file)
6. [Download File](#download-file)
7. [Check Status](#check-status)
8. [List Conversions](#list-conversions)
9. [Delete Conversion](#delete-conversion)
10. [Get Supported Formats](#get-supported-formats)
11. [Category-Specific Examples](#category-specific-examples)
12. [Error Handling](#error-handling)

---

## 🚀 Getting Started

### Base URL
```
http://localhost:8000
```

### API Documentation
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Quick Test
```bash
# Health check
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy"
}
```

---

## 🔐 Authentication

**Current Status**: No authentication required (open API)

**Coming Soon**: API key authentication for production deployments.

**Recommended for Production**:
```bash
# Future API key usage (not yet implemented)
curl -H "X-API-Key: your_api_key_here" http://localhost:8000/api/...
```

---

## ⏱️ Rate Limits

### Current Limits
- **Rate**: 10 requests per minute per IP address
- **File Size**: 50 MB maximum (configurable)
- **File Retention**: 1 hour (automatic cleanup)

### Rate Limit Headers
```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
X-RateLimit-Reset: 1643678400
```

### Handling Rate Limits

**When rate limited, you'll receive:**
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```
**Status Code**: `429 Too Many Requests`

**Solution**: Wait 60 seconds before retrying.

---

## 📤 Upload File

### Endpoint
```
POST /api/upload
```

### Basic Upload

#### cURL
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@document.pdf"
```

#### Python
```python
import requests

url = "http://localhost:8000/api/upload"
files = {"file": open("document.pdf", "rb")}

response = requests.post(url, files=files)
print(response.json())
```

#### JavaScript (Browser)
```javascript
async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8000/api/upload', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}

// Usage with file input
const fileInput = document.getElementById('fileInput');
const file = fileInput.files[0];
const result = await uploadFile(file);
console.log(result);
```

#### JavaScript (Node.js)
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('file', fs.createReadStream('document.pdf'));

axios.post('http://localhost:8000/api/upload', form, {
  headers: form.getHeaders()
})
.then(response => console.log(response.data))
.catch(error => console.error(error));
```

### Response
```json
{
  "id": 1,
  "original_filename": "document.pdf",
  "source_format": "pdf",
  "target_format": null,
  "status": "uploaded",
  "created_at": "2026-01-31T10:30:00",
  "file_size": 1048576,
  "ip_address": "127.0.0.1"
}
```

---

## 🔄 Convert File

Conversions are category-specific. Use the appropriate endpoint for your file type.

### Document Conversion

#### Endpoint
```
POST /api/documents/convert/{conversion_id}?target_format={format}
```

#### cURL
```bash
# PDF to DOCX
curl -X POST "http://localhost:8000/api/documents/convert/1?target_format=docx"

# DOCX to PDF
curl -X POST "http://localhost:8000/api/documents/convert/2?target_format=pdf"

# Excel to CSV
curl -X POST "http://localhost:8000/api/documents/convert/3?target_format=csv"
```

#### Python
```python
import requests

conversion_id = 1
target_format = "docx"

url = f"http://localhost:8000/api/documents/convert/{conversion_id}"
params = {"target_format": target_format}

response = requests.post(url, params=params)
print(response.json())
```

#### JavaScript
```javascript
async function convertDocument(conversionId, targetFormat) {
  const url = `http://localhost:8000/api/documents/convert/${conversionId}?target_format=${targetFormat}`;
  
  const response = await fetch(url, { method: 'POST' });
  return await response.json();
}

// Usage
const result = await convertDocument(1, 'docx');
console.log(result);
```

### Image Conversion

#### Endpoint
```
POST /api/images/convert/{conversion_id}?target_format={format}
```

#### Examples
```bash
# PNG to JPG
curl -X POST "http://localhost:8000/api/images/convert/1?target_format=jpg"

# JPG to WebP
curl -X POST "http://localhost:8000/api/images/convert/2?target_format=webp"

# HEIC to PNG
curl -X POST "http://localhost:8000/api/images/convert/3?target_format=png"
```

### Audio Conversion

#### Endpoint
```
POST /api/audio/convert/{conversion_id}?target_format={format}
```

#### Examples
```bash
# WAV to MP3
curl -X POST "http://localhost:8000/api/audio/convert/1?target_format=mp3"

# MP3 to WAV
curl -X POST "http://localhost:8000/api/audio/convert/2?target_format=wav"

# M4A to MP3
curl -X POST "http://localhost:8000/api/audio/convert/3?target_format=mp3"
```

### Video Conversion

#### Endpoint
```
POST /api/video/convert/{conversion_id}?target_format={format}
```

#### Examples
```bash
# MKV to MP4
curl -X POST "http://localhost:8000/api/video/convert/1?target_format=mp4"

# AVI to MP4
curl -X POST "http://localhost:8000/api/video/convert/2?target_format=mp4"

# MP4 to GIF
curl -X POST "http://localhost:8000/api/video/convert/3?target_format=gif"
```

### Response (All Conversions)
```json
{
  "id": 1,
  "original_filename": "document.pdf",
  "source_format": "pdf",
  "target_format": "docx",
  "status": "completed",
  "output_path": "/outputs/document_converted_12345.docx",
  "created_at": "2026-01-31T10:30:00",
  "completed_at": "2026-01-31T10:30:05"
}
```

---

## 📥 Download File

### Endpoint
```
GET /api/download/{conversion_id}
```

### Download Converted File

#### cURL
```bash
# Download and save to file
curl "http://localhost:8000/api/download/1" -o output.docx

# Download with original filename
curl -OJ "http://localhost:8000/api/download/1"
```

#### Python
```python
import requests

conversion_id = 1
url = f"http://localhost:8000/api/download/{conversion_id}"

response = requests.get(url)

# Save to file
with open("output.docx", "wb") as f:
    f.write(response.content)

print("File downloaded successfully")
```

#### JavaScript (Browser)
```javascript
async function downloadFile(conversionId, filename) {
  const url = `http://localhost:8000/api/download/${conversionId}`;
  
  const response = await fetch(url);
  const blob = await response.blob();
  
  // Create download link
  const link = document.createElement('a');
  link.href = window.URL.createObjectURL(blob);
  link.download = filename;
  link.click();
}

// Usage
await downloadFile(1, 'output.docx');
```

#### JavaScript (Node.js)
```javascript
const axios = require('axios');
const fs = require('fs');

async function downloadFile(conversionId, outputPath) {
  const url = `http://localhost:8000/api/download/${conversionId}`;
  
  const response = await axios.get(url, {
    responseType: 'stream'
  });
  
  const writer = fs.createWriteStream(outputPath);
  response.data.pipe(writer);
  
  return new Promise((resolve, reject) => {
    writer.on('finish', resolve);
    writer.on('error', reject);
  });
}

// Usage
await downloadFile(1, 'output.docx');
```

---

## 🔍 Check Status

### Endpoint
```
GET /api/conversions/{conversion_id}
```

### Check Conversion Status

#### cURL
```bash
curl "http://localhost:8000/api/conversions/1"
```

#### Python
```python
import requests

conversion_id = 1
url = f"http://localhost:8000/api/conversions/{conversion_id}"

response = requests.get(url)
conversion = response.json()

print(f"Status: {conversion['status']}")
print(f"Progress: {conversion.get('progress', 'N/A')}")
```

#### JavaScript
```javascript
async function checkStatus(conversionId) {
  const url = `http://localhost:8000/api/conversions/${conversionId}`;
  const response = await fetch(url);
  return await response.json();
}

// Polling example
async function waitForCompletion(conversionId) {
  while (true) {
    const status = await checkStatus(conversionId);
    
    if (status.status === 'completed') {
      return status;
    } else if (status.status === 'failed') {
      throw new Error(status.error_message);
    }
    
    await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
  }
}
```

### Response
```json
{
  "id": 1,
  "original_filename": "document.pdf",
  "source_format": "pdf",
  "target_format": "docx",
  "status": "completed",
  "progress": 100,
  "output_path": "/outputs/document_converted_12345.docx",
  "created_at": "2026-01-31T10:30:00",
  "completed_at": "2026-01-31T10:30:05",
  "file_size": 1048576
}
```

### Status Values
- `uploaded`: File uploaded, not yet converted
- `processing`: Conversion in progress
- `completed`: Conversion successful
- `failed`: Conversion failed

---

## 📋 List Conversions

### Endpoint
```
GET /api/conversions
```

### List All Conversions

#### cURL
```bash
# List all
curl "http://localhost:8000/api/conversions"

# With pagination
curl "http://localhost:8000/api/conversions?skip=0&limit=10"
```

#### Python
```python
import requests

url = "http://localhost:8000/api/conversions"
params = {"skip": 0, "limit": 10}

response = requests.get(url, params=params)
conversions = response.json()

for conv in conversions:
    print(f"{conv['id']}: {conv['original_filename']} - {conv['status']}")
```

#### JavaScript
```javascript
async function listConversions(skip = 0, limit = 10) {
  const url = `http://localhost:8000/api/conversions?skip=${skip}&limit=${limit}`;
  const response = await fetch(url);
  return await response.json();
}

// Usage
const conversions = await listConversions(0, 10);
conversions.forEach(conv => {
  console.log(`${conv.id}: ${conv.original_filename} - ${conv.status}`);
});
```

---

## 🗑️ Delete Conversion

### Endpoint
```
DELETE /api/conversions/{conversion_id}
```

### Delete a Conversion

#### cURL
```bash
curl -X DELETE "http://localhost:8000/api/conversions/1"
```

#### Python
```python
import requests

conversion_id = 1
url = f"http://localhost:8000/api/conversions/{conversion_id}"

response = requests.delete(url)
print(response.json())
```

#### JavaScript
```javascript
async function deleteConversion(conversionId) {
  const url = `http://localhost:8000/api/conversions/${conversionId}`;
  const response = await fetch(url, { method: 'DELETE' });
  return await response.json();
}

// Usage
await deleteConversion(1);
```

---

## 📋 Get Supported Formats

### Endpoint
```
GET /api/formats
```

### Get All Supported Formats

#### cURL
```bash
curl "http://localhost:8000/api/formats"
```

#### Response
```json
{
  "document": ["pdf", "doc", "docx", "txt", "rtf", "odt", "xls", "xlsx", "csv"],
  "image": ["jpg", "jpeg", "png", "webp", "tiff", "bmp", "heic", "svg", "ico"],
  "audio": ["mp3", "wav", "aac", "ogg", "flac", "m4a", "opus"],
  "video": ["mp4", "mkv", "avi", "mov", "flv", "wmv", "webm"],
  "archive": ["zip", "rar", "7z", "tar", "gz"],
  "code": ["json", "xml", "yaml", "csv", "md", "html"],
  "design": ["psd", "ai", "svg", "dwg", "dxf"],
  "database": ["sql", "parquet", "avro"]
}
```

---

## 🔧 Category-Specific Examples

### Complete Document Conversion Flow

#### Python Example
```python
import requests
import time

BASE_URL = "http://localhost:8000"

def convert_document(input_file, target_format):
    """Complete document conversion workflow"""
    
    # Step 1: Upload file
    print("Uploading file...")
    with open(input_file, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/api/upload", files=files)
    
    upload_data = response.json()
    conversion_id = upload_data['id']
    print(f"Upload complete. Conversion ID: {conversion_id}")
    
    # Step 2: Convert
    print(f"Converting to {target_format}...")
    response = requests.post(
        f"{BASE_URL}/api/documents/convert/{conversion_id}",
        params={"target_format": target_format}
    )
    
    # Step 3: Wait for completion (if needed)
    while True:
        response = requests.get(f"{BASE_URL}/api/conversions/{conversion_id}")
        status_data = response.json()
        
        if status_data['status'] == 'completed':
            print("Conversion complete!")
            break
        elif status_data['status'] == 'failed':
            raise Exception(f"Conversion failed: {status_data.get('error_message')}")
        
        time.sleep(1)
    
    # Step 4: Download result
    print("Downloading...")
    response = requests.get(f"{BASE_URL}/api/download/{conversion_id}")
    
    output_file = f"output.{target_format}"
    with open(output_file, 'wb') as f:
        f.write(response.content)
    
    print(f"Saved to {output_file}")
    return output_file

# Usage
convert_document("document.pdf", "docx")
```

### Image Batch Conversion

#### Python Example
```python
import requests
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"

def batch_convert_images(input_dir, target_format):
    """Convert all images in a directory"""
    
    results = []
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp']
    
    for file_path in Path(input_dir).glob('*'):
        if file_path.suffix.lower() in image_extensions:
            print(f"Converting {file_path.name}...")
            
            # Upload
            with open(file_path, 'rb') as f:
                response = requests.post(
                    f"{BASE_URL}/api/upload",
                    files={'file': f}
                )
            
            conversion_id = response.json()['id']
            
            # Convert
            requests.post(
                f"{BASE_URL}/api/images/convert/{conversion_id}",
                params={"target_format": target_format}
            )
            
            # Download
            response = requests.get(f"{BASE_URL}/api/download/{conversion_id}")
            
            output_path = f"output/{file_path.stem}.{target_format}"
            os.makedirs("output", exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            results.append(output_path)
            print(f"  → Saved to {output_path}")
    
    return results

# Usage
batch_convert_images("./images", "webp")
```

### Video to Audio Extraction

#### cURL Example
```bash
#!/bin/bash
# Extract audio from video file

# Upload video
UPLOAD_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/upload" \
  -F "file=@video.mp4")

CONVERSION_ID=$(echo $UPLOAD_RESPONSE | jq -r '.id')
echo "Conversion ID: $CONVERSION_ID"

# Convert to MP3
curl -X POST "http://localhost:8000/api/video/convert/$CONVERSION_ID?target_format=mp3"

# Wait a bit
sleep 5

# Download
curl "http://localhost:8000/api/download/$CONVERSION_ID" -o audio.mp3
echo "Audio extracted to audio.mp3"
```

### JSON to CSV Conversion

#### JavaScript Example
```javascript
const fs = require('fs');
const axios = require('axios');
const FormData = require('form-data');

async function jsonToCsv(jsonFile) {
  const BASE_URL = 'http://localhost:8000';
  
  // Upload JSON file
  const form = new FormData();
  form.append('file', fs.createReadStream(jsonFile));
  
  const uploadResponse = await axios.post(
    `${BASE_URL}/api/upload`,
    form,
    { headers: form.getHeaders() }
  );
  
  const conversionId = uploadResponse.data.id;
  console.log(`Uploaded. ID: ${conversionId}`);
  
  // Convert to CSV
  await axios.post(
    `${BASE_URL}/api/code/convert/${conversionId}?target_format=csv`
  );
  
  // Download CSV
  const downloadResponse = await axios.get(
    `${BASE_URL}/api/download/${conversionId}`,
    { responseType: 'stream' }
  );
  
  const writer = fs.createWriteStream('output.csv');
  downloadResponse.data.pipe(writer);
  
  return new Promise((resolve, reject) => {
    writer.on('finish', () => {
      console.log('Saved to output.csv');
      resolve();
    });
    writer.on('error', reject);
  });
}

// Usage
jsonToCsv('data.json');
```

---

## ❌ Error Handling

### Common Error Responses

#### File Too Large (413)
```json
{
  "detail": "File size exceeds maximum allowed size of 50MB"
}
```

#### Unsupported Format (400)
```json
{
  "detail": "Unsupported file format: xyz"
}
```

#### Conversion Not Found (404)
```json
{
  "detail": "Conversion not found"
}
```

#### Rate Limit Exceeded (429)
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

#### Conversion Failed (500)
```json
{
  "detail": "Conversion failed: Invalid file format"
}
```

### Error Handling Example

#### Python
```python
import requests
from requests.exceptions import RequestException

def safe_convert(file_path, target_format):
    try:
        # Upload
        with open(file_path, 'rb') as f:
            response = requests.post(
                "http://localhost:8000/api/upload",
                files={'file': f}
            )
        response.raise_for_status()
        
        conversion_id = response.json()['id']
        
        # Convert
        response = requests.post(
            f"http://localhost:8000/api/documents/convert/{conversion_id}",
            params={"target_format": target_format}
        )
        response.raise_for_status()
        
        return conversion_id
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 413:
            print("Error: File too large")
        elif e.response.status_code == 400:
            print(f"Error: {e.response.json()['detail']}")
        elif e.response.status_code == 429:
            print("Error: Rate limit exceeded. Please wait.")
        else:
            print(f"HTTP Error: {e}")
        return None
        
    except RequestException as e:
        print(f"Request failed: {e}")
        return None
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

#### JavaScript
```javascript
async function safeConvert(file, targetFormat) {
  try {
    // Upload
    const formData = new FormData();
    formData.append('file', file);
    
    let response = await fetch('http://localhost:8000/api/upload', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }
    
    const uploadData = await response.json();
    const conversionId = uploadData.id;
    
    // Convert
    response = await fetch(
      `http://localhost:8000/api/documents/convert/${conversionId}?target_format=${targetFormat}`,
      { method: 'POST' }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }
    
    return conversionId;
    
  } catch (error) {
    if (error.message.includes('File size exceeds')) {
      console.error('File too large');
    } else if (error.message.includes('Rate limit')) {
      console.error('Rate limit exceeded');
    } else {
      console.error('Conversion failed:', error.message);
    }
    return null;
  }
}
```

---

## 📊 Response Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid input or unsupported format |
| 404 | Not Found | Conversion or file not found |
| 413 | Payload Too Large | File exceeds size limit |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error during conversion |

---

## 🔗 API Endpoint Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/api/formats` | List supported formats |
| POST | `/api/upload` | Upload file |
| POST | `/api/{category}/convert/{id}` | Convert file |
| GET | `/api/download/{id}` | Download converted file |
| GET | `/api/conversions` | List all conversions |
| GET | `/api/conversions/{id}` | Get conversion status |
| DELETE | `/api/conversions/{id}` | Delete conversion |

---

## 💡 Best Practices

1. **Always check status** before downloading large conversions
2. **Handle errors gracefully** with proper try-catch blocks
3. **Respect rate limits** - implement exponential backoff
4. **Clean up** old conversions after downloading
5. **Validate files** before uploading to save bandwidth
6. **Use appropriate formats** for your use case
7. **Implement retries** for network failures
8. **Stream large files** instead of loading into memory

---

**Happy Coding! 🚀**

*API Version 1.0.0 - Updated January 2026*
