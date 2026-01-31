# Rapid Testing Script v2
$baseUrl = "http://localhost:8000"
$testLog = @()
$passCount = 0
$failCount = 0

function Write-TestResult {
    param($Status, $Message, $Details = "")
    Write-Host "$Status $Message" -ForegroundColor $(if($Status -eq "✅") {"Green"} else {"Red"})
    if ($Details) { Write-Host "   $Details" -ForegroundColor Gray }
    $script:testLog += "$Status $Message`n$Details`n"
}

function Test-Upload {
    param($FilePath)
    try {
        $form = @{file = Get-Item -Path $FilePath}
        $response = Invoke-RestMethod -Uri "$baseUrl/api/upload" -Method Post -Form $form
        return $response.id
    } catch {
        Write-Host "Upload Error: $_" -ForegroundColor Red
        return $null
    }
}

function Test-Convert {
    param($ConversionId, $Category, $TargetFormat, $RequestBody = @{})
    try {
        $url = "$baseUrl/api/$Category/convert/${ConversionId}?target_format=$TargetFormat"
        $response = Invoke-RestMethod -Uri $url -Method Post -Body ($RequestBody | ConvertTo-Json) -ContentType "application/json"
        return $response
    } catch {
        return @{error = $_.Exception.Message}
    }
}

Write-Host "`n🚀 YOLO MODE ACTIVATED - Testing Everything Fast!`n" -ForegroundColor Cyan

# ===== 1. DOCUMENTS =====
Write-Host "📄 DOCUMENTS" -ForegroundColor Yellow
$id = Test-Upload "test_files\test.txt"
if ($id) {
    $r = Test-Convert $id "documents" "pdf"
    if ($r.status -eq "completed") { Write-TestResult "✅" "TXT → PDF"; $script:passCount++ } else { Write-TestResult "❌" "TXT → PDF" $r.error; $script:failCount++ }
}

$id = Test-Upload "test_files\test.txt"
if ($id) {
    $r = Test-Convert $id "documents" "docx"
    if ($r.status -eq "completed") { Write-TestResult "✅" "TXT → DOCX"; $script:passCount++ } else { Write-TestResult "❌" "TXT → DOCX" $r.error; $script:failCount++ }
}

$id = Test-Upload "test_files\test.csv"
if ($id) {
    $r = Test-Convert $id "documents" "xlsx"
    if ($r.status -eq "completed") { Write-TestResult "✅" "CSV → XLSX"; $script:passCount++ } else { Write-TestResult "❌" "CSV → XLSX" $r.error; $script:failCount++ }
}

# ===== 2. CODE CONVERSIONS =====
Write-Host "`n💻 CODE" -ForegroundColor Yellow
$id = Test-Upload "test_files\test.json"
if ($id) {
    $r = Test-Convert $id "code" "xml"
    if ($r.status -eq "completed" -or $r.download_url) { Write-TestResult "✅" "JSON → XML"; $script:passCount++ } else { Write-TestResult "❌" "JSON → XML" $r.error; $script:failCount++ }
}

$id = Test-Upload "test_files\test.json"
if ($id) {
    $r = Test-Convert $id "code" "yaml"
    if ($r.status -eq "completed" -or $r.download_url) { Write-TestResult "✅" "JSON → YAML"; $script:passCount++ } else { Write-TestResult "❌" "JSON → YAML" $r.error; $script:failCount++ }
}

$id = Test-Upload "test_files\test.xml"
if ($id) {
    $r = Test-Convert $id "code" "json"
    if ($r.status -eq "completed" -or $r.download_url) { Write-TestResult "✅" "XML → JSON"; $script:passCount++ } else { Write-TestResult "❌" "XML → JSON" $r.error; $script:failCount++ }
}

$id = Test-Upload "test_files\test.csv"
if ($id) {
    $r = Test-Convert $id "code" "json"
    if ($r.status -eq "completed" -or $r.download_url) { Write-TestResult "✅" "CSV → JSON"; $script:passCount++ } else { Write-TestResult "❌" "CSV → JSON" $r.error; $script:failCount++ }
}

# ===== 3. SECURITY =====
Write-Host "`n🔒 SECURITY" -ForegroundColor Yellow
$id = Test-Upload "test_files\test.txt"
if ($id) {
    $r = Test-Convert $id "security" "base64"
    if ($r.status -eq "completed" -or $r.download_url) { Write-TestResult "✅" "Base64 Encode"; $script:passCount++ } else { Write-TestResult "❌" "Base64 Encode" $r.error; $script:failCount++ }
}

$id = Test-Upload "test_files\test.txt"
if ($id) {
    $r = Test-Convert $id "security" "md5"
    if ($r.status -eq "completed" -or $r.download_url -or $r.result) { Write-TestResult "✅" "MD5 Hash"; $script:passCount++ } else { Write-TestResult "❌" "MD5 Hash" $r.error; $script:failCount++ }
}

$id = Test-Upload "test_files\test.txt"
if ($id) {
    $r = Test-Convert $id "security" "sha256"
    if ($r.status -eq "completed" -or $r.download_url -or $r.result) { Write-TestResult "✅" "SHA256 Hash"; $script:passCount++ } else { Write-TestResult "❌" "SHA256 Hash" $r.error; $script:failCount++ }
}

# ===== SUMMARY =====
Write-Host "`n" + ("="*60) -ForegroundColor Cyan
Write-Host "📊 TEST SUMMARY" -ForegroundColor Cyan
Write-Host ("="*60) -ForegroundColor Cyan
Write-Host "✅ Passed: $passCount" -ForegroundColor Green
Write-Host "❌ Failed: $failCount" -ForegroundColor Red
Write-Host "📈 Pass Rate: $([math]::Round(($passCount/($passCount+$failCount))*100, 1))%" -ForegroundColor Cyan
