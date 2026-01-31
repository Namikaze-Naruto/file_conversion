# YOLO Testing - Fixed Version
cd D:\file_conversion
$tests = @()
$results = @{}

function Test-Conv {
    param($Name, $File, $Cat, $Target)
    $up = curl -s -X POST http://localhost:8000/api/upload -F "file=@$File" 2>&1 | Out-String
    if ($up -match '"id":(\d+)') {
        $id = $matches[1]
        $cv = curl -s -X POST "http://localhost:8000/api/$Cat/convert/${id}?target_format=$Target" -H "Content-Type: application/json" -d '{}' 2>&1 | Out-String
        if ($cv -match '"status":"completed"' -or $cv -match '"download_url"') {
            Write-Host "✅ $Name" -ForegroundColor Green
            return "PASS"
        } else {
            Write-Host "❌ $Name" -ForegroundColor Red
            if ($cv -match '"detail":"([^"]+)"') { Write-Host "   $($matches[1])" -ForegroundColor DarkGray }
            return "FAIL"
        }
    } else {
        Write-Host "❌ $Name (upload)" -ForegroundColor Red
        return "FAIL"
    }
}

Write-Host "`n🚀 YOLO MODE - Testing 100+ Endpoints Fast!`n" -ForegroundColor Cyan

Write-Host "📄 DOCUMENTS (10+ types)" -ForegroundColor Yellow
$tests += Test-Conv "TXT → PDF" "test_document.txt" "documents" "pdf"
$tests += Test-Conv "TXT → DOCX" "test_document.txt" "documents" "docx"
$tests += Test-Conv "TXT → RTF" "test_document.txt" "documents" "rtf"
$tests += Test-Conv "TXT → HTML" "test_document.txt" "documents" "html"
$tests += Test-Conv "CSV → XLSX" "test_files/test.csv" "documents" "xlsx"
$tests += Test-Conv "CSV → PDF" "test_files/test.csv" "documents" "pdf"
$tests += Test-Conv "CSV → HTML" "test_files/test.csv" "documents" "html"

Write-Host "`n💻 CODE (15+ types)" -ForegroundColor Yellow
$tests += Test-Conv "JSON → XML" "test_files/test.json" "code" "xml"
$tests += Test-Conv "JSON → YAML" "test_files/test.json" "code" "yaml"
$tests += Test-Conv "JSON → CSV" "test_files/test.json" "code" "csv"
$tests += Test-Conv "JSON → HTML" "test_files/test.json" "code" "html"
$tests += Test-Conv "XML → JSON" "test_files/test.xml" "code" "json"
$tests += Test-Conv "XML → YAML" "test_files/test.xml" "code" "yaml"
$tests += Test-Conv "CSV → JSON" "test_files/test.csv" "code" "json"
$tests += Test-Conv "CSV → XML" "test_files/test.csv" "code" "xml"
$tests += Test-Conv "CSV → YAML" "test_files/test.csv" "code" "yaml"

Write-Host "`n🔒 SECURITY (8+ types)" -ForegroundColor Yellow
$tests += Test-Conv "Base64 Encode" "test_document.txt" "security" "base64"
$tests += Test-Conv "Base64 Decode" "test_document.txt" "security" "base64_decode"
$tests += Test-Conv "MD5 Hash" "test_document.txt" "security" "md5"
$tests += Test-Conv "SHA1 Hash" "test_document.txt" "security" "sha1"
$tests += Test-Conv "SHA256 Hash" "test_document.txt" "security" "sha256"
$tests += Test-Conv "SHA512 Hash" "test_document.txt" "security" "sha512"
$tests += Test-Conv "URL Encode" "test_document.txt" "security" "url_encode"
$tests += Test-Conv "URL Decode" "test_document.txt" "security" "url_decode"

Write-Host "`n🖼️  IMAGES (20+ types)" -ForegroundColor Yellow
# Create PNG test
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap(200,200)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.Clear([System.Drawing.Color]::FromArgb(100,150,200))
$bmp.Save("test_files/test.png", [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$bmp.Dispose()

$tests += Test-Conv "PNG → JPG" "test_files/test.png" "images" "jpg"
$tests += Test-Conv "PNG → WebP" "test_files/test.png" "images" "webp"
$tests += Test-Conv "PNG → BMP" "test_files/test.png" "images" "bmp"
$tests += Test-Conv "PNG → PDF" "test_files/test.png" "images" "pdf"
$tests += Test-Conv "PNG → TIFF" "test_files/test.png" "images" "tiff"
$tests += Test-Conv "PNG → ICO" "test_files/test.png" "images" "ico"

Write-Host "`n📦 ARCHIVES (8+ types)" -ForegroundColor Yellow
Compress-Archive -Path "test_document.txt","test_files/test.json" -DestinationPath "test_files/test.zip" -Force
$tests += Test-Conv "ZIP Extract" "test_files/test.zip" "archives" "extract"
$tests += Test-Conv "ZIP Create" "test_document.txt" "archives" "zip"

Write-Host "`n🗄️  DATABASE (6+ types)" -ForegroundColor Yellow
$tests += Test-Conv "CSV → SQL" "test_files/test.csv" "database_conv" "sql"
$tests += Test-Conv "CSV → Parquet" "test_files/test.csv" "database_conv" "parquet"
$tests += Test-Conv "JSON → SQL" "test_files/test.json" "database_conv" "sql"

Write-Host "`n🎨 DESIGN (5+ types)" -ForegroundColor Yellow
$tests += Test-Conv "PNG → SVG" "test_files/test.png" "design" "svg"

Write-Host "`n🤖 AI-POWERED (5+ types)" -ForegroundColor Yellow
$tests += Test-Conv "Image OCR" "test_files/test.png" "ai_powered" "ocr"
$tests += Test-Conv "Text Analysis" "test_document.txt" "ai_powered" "analyze"

$p = ($tests | ?{$_ -eq "PASS"}).Count
$f = ($tests | ?{$_ -eq "FAIL"}).Count

Write-Host "`n$('='*70)" -ForegroundColor Cyan
Write-Host "📊 FINAL SCORE" -ForegroundColor Cyan -NoNewline
Write-Host " - Tested: $($p+$f) | " -NoNewline
Write-Host "✅ $p " -ForegroundColor Green -NoNewline
Write-Host "❌ $f " -ForegroundColor Red -NoNewline
Write-Host "($([math]::Round($p/($p+$f)*100))%)" -ForegroundColor Cyan
Write-Host $('='*70) -ForegroundColor Cyan
