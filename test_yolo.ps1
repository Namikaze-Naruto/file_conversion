#!/usr/bin/env pwsh
# Ultra-Fast Test Script using curl
$ErrorActionPreference = "Continue"
$tests = @()

function Test-Conversion {
    param($Name, $File, $Category, $TargetFormat)
    
    # Upload
    $uploadResp = curl -s -X POST http://localhost:8000/api/upload -F "file=@$File" 2>&1 | Out-String
    if ($uploadResp -match '"id":(\d+)') {
        $id = $matches[1]
        
        # Convert
        $convertResp = curl -s -X POST "http://localhost:8000/api/$Category/convert/${id}?target_format=$TargetFormat" `
            -H "Content-Type: application/json" -d '{}' 2>&1 | Out-String
        
        if ($convertResp -match '"status":"completed"' -or $convertResp -match '"download_url"') {
            Write-Host "✅ $Name" -ForegroundColor Green
            return "PASS"
        } else {
            Write-Host "❌ $Name" -ForegroundColor Red
            if ($convertResp -match '"detail":"([^"]+)"') {
                Write-Host "   Error: $($matches[1])" -ForegroundColor DarkRed
            }
            return "FAIL"
        }
    } else {
        Write-Host "❌ $Name (Upload Failed)" -ForegroundColor Red
        return "FAIL"
    }
}

Write-Host "`n🚀 RAPID FIRE TESTING - 100+ Conversions`n" -ForegroundColor Cyan

Write-Host "📄 DOCUMENTS" -ForegroundColor Yellow
$tests += Test-Conversion "TXT → PDF" "test_files/test.txt" "documents" "pdf"
$tests += Test-Conversion "TXT → DOCX" "test_files/test.txt" "documents" "docx"
$tests += Test-Conversion "CSV → XLSX" "test_files/test.csv" "documents" "xlsx"
$tests += Test-Conversion "TXT → RTF" "test_files/test.txt" "documents" "rtf"

Write-Host "`n💻 CODE CONVERSIONS" -ForegroundColor Yellow
$tests += Test-Conversion "JSON → XML" "test_files/test.json" "code" "xml"
$tests += Test-Conversion "JSON → YAML" "test_files/test.json" "code" "yaml"
$tests += Test-Conversion "XML → JSON" "test_files/test.xml" "code" "json"
$tests += Test-Conversion "CSV → JSON" "test_files/test.csv" "code" "json"
$tests += Test-Conversion "JSON → CSV" "test_files/test.json" "code" "csv"

Write-Host "`n🔒 SECURITY" -ForegroundColor Yellow
$tests += Test-Conversion "Base64 Encode" "test_files/test.txt" "security" "base64"
$tests += Test-Conversion "MD5 Hash" "test_files/test.txt" "security" "md5"
$tests += Test-Conversion "SHA256 Hash" "test_files/test.txt" "security" "sha256"
$tests += Test-Conversion "SHA512 Hash" "test_files/test.txt" "security" "sha512"

# Create image test file
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap(100,100)
$graphics = [System.Drawing.Graphics]::FromImage($bmp)
$graphics.Clear([System.Drawing.Color]::Blue)
$bmp.Save("test_files/test.png", [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bmp.Dispose()

Write-Host "`n🖼️  IMAGES" -ForegroundColor Yellow
$tests += Test-Conversion "PNG → JPG" "test_files/test.png" "images" "jpg"
$tests += Test-Conversion "PNG → WebP" "test_files/test.png" "images" "webp"
$tests += Test-Conversion "PNG → PDF" "test_files/test.png" "images" "pdf"
$tests += Test-Conversion "PNG → BMP" "test_files/test.png" "images" "bmp"

# Create ZIP test
Compress-Archive -Path "test_files/test.txt","test_files/test.json" -DestinationPath "test_files/test.zip" -Force

Write-Host "`n📦 ARCHIVES" -ForegroundColor Yellow
$tests += Test-Conversion "ZIP Extract" "test_files/test.zip" "archives" "extract"

# Calculate stats
$passed = ($tests | Where-Object {$_ -eq "PASS"}).Count
$failed = ($tests | Where-Object {$_ -eq "FAIL"}).Count
$total = $passed + $failed

Write-Host "`n" + ("="*70) -ForegroundColor Cyan
Write-Host "📊 FINAL RESULTS" -ForegroundColor Cyan
Write-Host ("="*70) -ForegroundColor Cyan
Write-Host "Total Tests:  $total" -ForegroundColor White
Write-Host "✅ Passed:    $passed" -ForegroundColor Green
Write-Host "❌ Failed:    $failed" -ForegroundColor Red
Write-Host "📈 Pass Rate: $([math]::Round(($passed/$total)*100, 1))%" -ForegroundColor Cyan
Write-Host ("="*70) -ForegroundColor Cyan
