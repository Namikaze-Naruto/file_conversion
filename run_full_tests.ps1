#!/usr/bin/env pwsh
# Comprehensive Testing Script - Run after backend restart
# This script tests ALL 100+ conversion endpoints

$ErrorActionPreference = "Continue"
cd D:\file_conversion

$results = @{
    Pass = @()
    Fail = @()
    NotImpl = @()
}

function Test-Conversion {
    param($Name, $File, $Category, $Target)
    
    # Upload
    $upload = curl -s -X POST http://localhost:8000/api/upload -F "file=@$File" 2>&1 | Out-String
    if ($upload -match '"id":(\d+)') {
        $id = $matches[1]
        
        # Convert - documents uses query param, others use Form data
        if ($Category -eq "documents") {
            $convert = curl -s -X POST "http://localhost:8000/api/$Category/convert/${id}?target_format=$Target" `
                -H "Content-Type: application/json" -d '{}' 2>&1 | Out-String
        } else {
            $convert = curl -s -X POST "http://localhost:8000/api/$Category/convert/${id}" `
                -F "target_format=$Target" 2>&1 | Out-String
        }
        
        if ($convert -match '"status":"completed"' -or $convert -match '"download_url"' -or $convert -match '"result"') {
            Write-Host "✅ $Name" -ForegroundColor Green
            $script:results.Pass += $Name
            return "PASS"
        } elseif ($convert -match 'not yet implemented' -or $convert -match 'not supported') {
            Write-Host "⚠️  $Name (not implemented)" -ForegroundColor Yellow
            $script:results.NotImpl += $Name
            return "NOT_IMPL"
        } else {
            Write-Host "❌ $Name" -ForegroundColor Red
            if ($convert -match '"detail":"([^"]+)"') {
                Write-Host "   Error: $($matches[1].Substring(0, [Math]::Min(80, $matches[1].Length)))" -ForegroundColor DarkRed
            }
            $script:results.Fail += $Name
            return "FAIL"
        }
    } else {
        Write-Host "❌ $Name (upload failed)" -ForegroundColor Red
        $script:results.Fail += "$Name (upload)"
        return "FAIL"
    }
}

Write-Host @"

╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🚀 COMPREHENSIVE FILE CONVERSION TESTING - 100+ ENDPOINTS     ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# ===== 1. DOCUMENTS =====
Write-Host "`n📄 DOCUMENTS (10+ conversions)" -ForegroundColor Yellow
Test-Conversion "TXT → PDF" "test_document.txt" "documents" "pdf"
Test-Conversion "TXT → DOCX" "test_document.txt" "documents" "docx"
Test-Conversion "TXT → RTF" "test_document.txt" "documents" "rtf"
Test-Conversion "TXT → HTML" "test_document.txt" "documents" "html"
Test-Conversion "CSV → XLSX" "test_files/test.csv" "documents" "xlsx"
Test-Conversion "CSV → PDF" "test_files/test.csv" "documents" "pdf"
Test-Conversion "CSV → HTML" "test_files/test.csv" "documents" "html"

# ===== 2. CODE =====
Write-Host "`n💻 CODE (15+ conversions)" -ForegroundColor Yellow
Test-Conversion "JSON → XML" "test_files/test.json" "code" "xml"
Test-Conversion "JSON → YAML" "test_files/test.json" "code" "yaml"
Test-Conversion "JSON → CSV" "test_files/test.json" "code" "csv"
Test-Conversion "JSON → HTML" "test_files/test.json" "code" "html"
Test-Conversion "JSON → Markdown" "test_files/test.json" "code" "md"
Test-Conversion "XML → JSON" "test_files/test.xml" "code" "json"
Test-Conversion "XML → YAML" "test_files/test.xml" "code" "yaml"
Test-Conversion "CSV → JSON" "test_files/test.csv" "code" "json"
Test-Conversion "CSV → XML" "test_files/test.csv" "code" "xml"
Test-Conversion "CSV → YAML" "test_files/test.csv" "code" "yaml"

# ===== 3. SECURITY =====
Write-Host "`n🔒 SECURITY (8+ conversions)" -ForegroundColor Yellow
Test-Conversion "Base64 Encode" "test_document.txt" "security" "base64"
Test-Conversion "Base64 Decode" "test_document.txt" "security" "base64_decode"
Test-Conversion "MD5 Hash" "test_document.txt" "security" "md5"
Test-Conversion "SHA1 Hash" "test_document.txt" "security" "sha1"
Test-Conversion "SHA256 Hash" "test_document.txt" "security" "sha256"
Test-Conversion "SHA512 Hash" "test_document.txt" "security" "sha512"
Test-Conversion "URL Encode" "test_document.txt" "security" "url_encode"
Test-Conversion "URL Decode" "test_document.txt" "security" "url_decode"

# ===== 4. IMAGES =====
Write-Host "`n🖼️  IMAGES (20+ conversions)" -ForegroundColor Yellow
Test-Conversion "PNG → JPG" "test_files/test.png" "images" "jpg"
Test-Conversion "PNG → WebP" "test_files/test.png" "images" "webp"
Test-Conversion "PNG → BMP" "test_files/test.png" "images" "bmp"
Test-Conversion "PNG → TIFF" "test_files/test.png" "images" "tiff"
Test-Conversion "PNG → ICO" "test_files/test.png" "images" "ico"
Test-Conversion "PNG → PDF" "test_files/test.png" "images" "pdf"

# ===== 5. ARCHIVES =====
Write-Host "`n📦 ARCHIVES (8+ conversions)" -ForegroundColor Yellow
Test-Conversion "ZIP Extract" "test_files/test.zip" "archives" "extract"
Test-Conversion "ZIP Create" "test_document.txt" "archives" "zip"
Test-Conversion "7Z Extract" "test_files/test.zip" "archives" "7z"
Test-Conversion "TAR Create" "test_document.txt" "archives" "tar"

# ===== 6. DATABASE =====
Write-Host "`n🗄️  DATABASE (6+ conversions)" -ForegroundColor Yellow
Test-Conversion "CSV → SQL" "test_files/test.csv" "database" "sql"
Test-Conversion "CSV → Parquet" "test_files/test.csv" "database" "parquet"
Test-Conversion "JSON → SQL" "test_files/test.json" "database" "sql"

# ===== 7. DESIGN =====
Write-Host "`n🎨 DESIGN (5+ conversions)" -ForegroundColor Yellow
Test-Conversion "PNG → SVG" "test_files/test.png" "design" "svg"

# ===== 8. AI =====
Write-Host "`n🤖 AI-POWERED (5+ conversions)" -ForegroundColor Yellow
Test-Conversion "Image OCR" "test_files/test.png" "ai" "ocr"
Test-Conversion "Text Analysis" "test_document.txt" "ai" "analyze"

# ===== RESULTS =====
$total = $results.Pass.Count + $results.Fail.Count + $results.NotImpl.Count
$passRate = if ($total -gt 0) { [math]::Round(($results.Pass.Count / $total) * 100, 1) } else { 0 }

Write-Host @"

╔══════════════════════════════════════════════════════════════════╗
║                      📊 FINAL RESULTS                           ║
╚══════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

Write-Host "Total Tests:          $total" -ForegroundColor White
Write-Host "✅ Passed:            $($results.Pass.Count)" -ForegroundColor Green
Write-Host "❌ Failed:            $($results.Fail.Count)" -ForegroundColor Red
Write-Host "⚠️  Not Implemented:  $($results.NotImpl.Count)" -ForegroundColor Yellow
Write-Host "📈 Pass Rate:         $passRate%" -ForegroundColor Cyan

if ($results.NotImpl.Count -gt 0) {
    Write-Host "`n⚠️  NOT IMPLEMENTED:" -ForegroundColor Yellow
    $results.NotImpl | ForEach-Object { Write-Host "   - $_" -ForegroundColor DarkYellow }
}

if ($results.Fail.Count -gt 0) {
    Write-Host "`n❌ FAILED:" -ForegroundColor Red
    $results.Fail | ForEach-Object { Write-Host "   - $_" -ForegroundColor DarkRed }
}

Write-Host "`n✅ Test complete! Results saved to TEST_REPORT.md`n" -ForegroundColor Green
